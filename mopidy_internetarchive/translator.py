from __future__ import unicode_literals

import datetime
import itertools
import logging
import re

from mopidy import models

import uritools

from . import Extension

__all__ = (
    'parse_bitrate',
    'parse_date',
    'parse_length',
    'parse_mtime',
    'parse_track',
    'parse_creator'
)

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

QUERY_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')

SCHEME = Extension.ext_name

logger = logging.getLogger(__name__)


def parse_bitrate(string, default=None):
    if string:
        try:
            return int(float(string))
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
        return [models.Artist(name=obj)]
    else:
        return [models.Artist(name=name) for name in obj]


def ref(metadata):
    identifier = metadata['identifier']
    name = metadata.get('title', identifier)
    uri = uritools.uricompose(SCHEME, path=identifier)

    if metadata.get('mediatype', 'collection') != 'collection':
        return models.Ref.album(uri=uri, name=name)
    elif name in metadata.get('creator', []):
        return models.Ref.artist(uri=uri, name=name)
    else:
        return models.Ref.directory(uri=uri, name=name)


def album(metadata, images=[]):
    identifier = metadata['identifier']
    uri = uritools.uricompose(SCHEME, path=identifier)
    name = metadata.get('title', identifier)
    artists = parse_creator(metadata.get('creator'))
    date = parse_date(metadata.get('date'))
    return models.Album(
        uri=uri,
        name=name,
        artists=artists,
        date=date,
        images=images
    )


def track(metadata, file, album):
    identifier = metadata['identifier']
    filename = file['name']
    uri = uritools.uricompose(SCHEME, path=identifier, fragment=filename)
    name = file.get('title', filename)
    return models.Track(
        uri=uri,
        name=name,
        album=album,
        artists=album.artists,
        track_no=parse_track(file.get('track')),
        date=parse_date(file.get('date'), album.date),
        length=parse_length(file.get('length')),
        bitrate=parse_bitrate(file.get('bitrate')),
        last_modified=parse_mtime(file.get('mtime'))
    )


def query(*args, **kwargs):
    terms = []
    for field, value in itertools.chain(args, kwargs.items()):
        if not value:
            continue
        elif isinstance(value, basestring):
            values = [_quote(value)]
        else:
            values = [_quote(v) for v in value]
        if len(values) == 1:
            term = values[0]
        else:
            term = '(%s)' % ' OR '.join(values)
        terms.append(field + ':' + term if field else term)
    return ' AND '.join(terms)


def _quote(term):
    term = QUERY_CHAR_RE.sub(r'\\\1', term)
    # only quote if term contains whitespace, since date:"2014-01-01"
    # will raise an error
    if any(c.isspace() for c in term):
        term = '"' + term + '"'
    return term
