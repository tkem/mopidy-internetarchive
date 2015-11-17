from __future__ import unicode_literals

import datetime
import logging
import re

from mopidy.models import Album, Artist, Ref, Track

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


def parse_creator(obj, default=None):
    if not obj or obj == 'tmp':
        return default
    elif isinstance(obj, basestring):
        return [Artist(name=obj)]
    else:
        return [Artist(name=name) for name in obj]


def uri(identifier=None, filename=None, q=None):
    if q:
        return uritools.uricompose(Extension.ext_name, query={'q': q})
    elif filename:
        return '%s:%s#%s' % (Extension.ext_name, identifier, filename)
    else:
        return '%s:%s' % (Extension.ext_name, identifier)


def ref(obj, uri=uri):
    identifier = obj['identifier']
    mediatype = obj['mediatype']
    name = obj.get('title', identifier)

    if mediatype == 'search':
        return Ref.directory(name=name, uri=uri(q=identifier))
    elif mediatype != 'collection':
        return Ref.album(name=name, uri=uri(identifier))
    elif name in obj.get('creator', []):
        return Ref.artist(name=name, uri=uri(identifier))
    else:
        return Ref.directory(name=name, uri=uri(identifier))


def album(obj, images=[], uri=uri):
    identifier = obj['identifier']

    return Album(
        uri=uri(identifier),
        name=obj.get('title', identifier),
        artists=parse_creator(obj.get('creator')),
        date=parse_date(obj.get('date')),
        images=images
    )


def track(obj, file, album, uri=uri):
    identifier = obj['identifier']
    filename = file['name']

    return Track(
        uri=uri(identifier, filename),
        name=file.get('title', filename),
        album=album,
        artists=album.artists,
        track_no=parse_track(file.get('track')),
        date=parse_date(file.get('date'), album.date),
        length=parse_length(file.get('length')),
        bitrate=parse_bitrate(file.get('bitrate')),
        last_modified=parse_mtime(file.get('mtime'))
    )


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
        elif parts.query or parts.fragment:
            raise ValueError('Cannot search "%s"' % uri)
        else:
            pass  # root uri?
    if collections:
        terms.append('collection:(%s)' % ' OR '.join(collections))
    return ' AND '.join(terms)


def quote(value, re=re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')):
    return '"%s"' % re.sub(r'\\\1', value)
