from __future__ import unicode_literals

import collections
import datetime
import logging
import re

from mopidy.models import Album, Artist, Image, Ref, Track

import uritools

from . import Extension

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

ISODATE_RE = re.compile(r"""
(\d{4})
(?:\-(\d{2}))?
(?:\-(\d{2}))?
""", flags=re.VERBOSE)

_QUERYMAP = {
    'any': lambda values: (
        ' AND '.join(map(quote, values))
    ),
    'album': lambda values: (
        'title:(%s)' % ' '.join(map(quote, values))
    ),
    'albumartist': lambda values: (
        'creator:(%s)' % ' '.join(map(quote, values))
    ),
    'artist': lambda values: (
        'creator:(%s)' % ' '.join(map(quote, values))
    ),
    'date': lambda values: (
        # TODO: sanitize, not quote date! date:(2014-01-01) gives error
        ' AND '.join('date:%s' % quote(value) for value in values)
    )
}

logger = logging.getLogger(__name__)


def parse_bitrate(string, default=None):
    if string:
        try:
            return int(float(string) * 1000)
        except:
            logger.warn('Invalid Internet Archive bitrate: %r', string)
    return default


def parse_date(string, default=None):
    if string:
        try:
            return '-'.join(ISODATE_RE.match(string).groups('01'))
        except:
            logger.warn('Invalid Internet Archive date: %r', string)
    return default


def parse_length(string, default=None):
    if string:
        try:
            groups = DURATION_RE.match(string).groupdict('0')
            d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
            return int(d.total_seconds() * 1000)
        except:
            logger.warn('Invalid Internet Archive length: %r', string)
    return default


def parse_mtime(string, default=None):
    if string:
        try:
            return int(string)
        except:
            logger.warn('Invalid Internet Archive mtime: %r', string)
    return default


def parse_track(string, default=None):
    if string:
        try:
            return int(string.partition('/')[0])
        except:
            logger.warn('Invalid Internet Archive track: %r', string)
    return default


def parse_uri(uri):
    parts = uritools.urisplit(uri)
    return parts.path, parts.getfragment(), parts.getquerydict()


def uri(identifier='', filename=None, scheme=Extension.ext_name, **kwargs):
    if filename:
        return uritools.uricompose(scheme, path=identifier, fragment=filename)
    elif kwargs:
        return uritools.uricompose(scheme, path=identifier, query=kwargs)
    else:
        return '%s:%s' % (scheme, identifier)


def name(obj):
    title = obj.get('title')
    if isinstance(title, basestring):
        return title
    elif hasattr(title, '__getitem__'):
        return title[0]
    else:
        return obj.get('identifier')


def ref(obj, uri=uri):
    identifier = obj['identifier']
    mediatype = obj['mediatype']
    if mediatype == 'collection':
        return Ref.directory(name=name(obj), uri=uri(identifier))
    else:
        return Ref.album(name=name(obj), uri=uri(identifier))


def artists(obj):
    artist = obj.get('artist', obj.get('creator'))
    if not artist:
        return None
    elif isinstance(artist, basestring):
        return [Artist(name=artist)]
    else:
        return [Artist(name=name) for name in artist]


def album(obj, uri=uri):
    return Album(
        uri=uri(obj['identifier']),
        name=name(obj),
        artists=artists(obj),
        date=parse_date(obj.get('date'))
    )


def files(item, formats):
    byname = {}
    byformat = collections.defaultdict(list)
    for obj in item['files']:
        byname[obj['name']] = obj
        byformat[obj['format']].append(obj)
    try:
        files = next(byformat[f] for f in formats if f in byformat)
    except StopIteration:
        return []
    else:
        return [dict(byname.get(f.get('original'), {}), **f) for f in files]


def images(item, formats, uri=uri):
    identifier = item['metadata']['identifier']
    images = []
    for obj in files(item, formats):
        images.append(Image(uri=uri(identifier, obj['name'])))
    return images


def tracks(item, formats, uri=uri):
    identifier = item['metadata']['identifier']
    track = Track(album=album(item['metadata']))
    tracks = []
    for obj in files(item, formats):
        filename = obj.get('name')
        tracks.append(track.replace(
            uri=uri(identifier, filename),
            name=obj.get('title', filename),
            artists=artists(obj) or track.album.artists,
            genre=obj.get('genre'),
            track_no=parse_track(obj.get('track')),
            length=parse_length(obj.get('length')),
            bitrate=parse_bitrate(obj.get('bitrate')),
            last_modified=parse_mtime(obj.get('mtime'))
        ))
    return tracks


def query(query, uris=None, exact=False):
    if exact:
        raise ValueError('Exact queries not supported')
    terms = []
    for key, values in (query.iteritems() if query else []):
        try:
            term = _QUERYMAP[key](values)
        except KeyError:
            raise ValueError('Keyword "%s" not supported' % key)
        else:
            terms.append(term)
    collections = []
    for uri in uris or []:
        parts = uritools.urisplit(uri)
        if parts.path:
            collections.append(parts.path)
        elif not parts.query and not parts.fragment:
            pass  # root URI?
        else:
            raise ValueError('Cannot search "%s"' % uri)
    if collections:
        terms.append('collection:(%s)' % ' OR '.join(collections))
    return ' AND '.join(terms)


def quote(value, re=re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')):
    return '"%s"' % re.sub(r'\\\1', value)
