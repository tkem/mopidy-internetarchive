from __future__ import unicode_literals

import cachetools
import collections
import itertools
import logging
import operator
import re

from mopidy import backend
from mopidy.models import Album, Artist, Track, SearchResult, Ref
from uritools import uricompose, urisplit

from . import Extension
from .parsing import *  # noqa
from .query import Query

_URI_PREFIX = Extension.ext_name + ':'

_QUERY_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')

_QUERY_MAPPING = {
    'any': None,
    'album': 'title',
    'albumartist': 'creator',
    'date': 'date'
}

logger = logging.getLogger(__name__)


def _cache(cache_size=None, cache_ttl=None, **kwargs):
    """Cache factory"""
    if cache_size is None:
        return None  # mainly for testing/debugging
    elif cache_ttl is None:
        return cachetools.LRUCache(cache_size)
    else:
        return cachetools.TTLCache(cache_size, cache_ttl)


def _ref(metadata):
    identifier = metadata['identifier']
    uri = _URI_PREFIX + identifier
    name = metadata.get('title', identifier)
    if metadata.get('mediatype', 'collection') == 'collection':
        return Ref.directory(uri=uri, name=name)
    else:
        return Ref.album(uri=uri, name=name)


def _artists(metadata, default=[]):
    creator = metadata.get('creator')
    if not creator:
        return default
    elif isinstance(creator, basestring):
        return [Artist(name=creator)]
    else:
        return [Artist(name=name) for name in creator]


def _album(metadata, images=[]):
    identifier = metadata['identifier']
    uri = _URI_PREFIX + identifier
    name = metadata.get('title', identifier)
    artists = _artists(metadata)
    date = parse_date(metadata.get('date'))
    return Album(uri=uri, name=name, artists=artists, date=date, images=images)


def _track(metadata, file, album):
    identifier = metadata['identifier']
    filename = file['name']
    uri = _URI_PREFIX + identifier + '#' + filename
    name = file.get('title', filename)
    return Track(
        uri=uri,
        name=name,
        album=album,
        artists=_artists(file, album.artists),
        track_no=parse_track_no(file.get('track')),
        date=parse_date(file.get('date'), album.date),
        length=parse_length(file.get('length')),
        bitrate=parse_bitrate(file.get('bitrate')),
        # FIXME: comment=metadata.get('description'),
        last_modified=parse_mtime(file.get('mtime'))
    )


def _getfirstitem(object, keys, default=None):
    for key in keys:
        if key in object:
            return object[key]
    return default


def _quote(term):
    term = _QUERY_CHAR_RE.sub(r'\\\1', term)
    # only quote if term contains whitespace, since date:"2014-01-01"
    # will raise an error
    if any(c.isspace() for c in term):
        term = '"' + term + '"'
    return term


def _query(*args, **kwargs):
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


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(
        uri=_URI_PREFIX,
        name='Internet Archive'
    )

    def __init__(self, config, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self._config = iaconfig = config[Extension.ext_name]
        self._search_filter = {
            'format': iaconfig['audio_formats'],
            '-collection': iaconfig['exclude_collections'],
            '-mediatype': iaconfig['exclude_mediatypes']
        }
        self._cache = _cache(**iaconfig)
        self._tracks = {}  # track cache for faster lookup

    def lookup(self, uri):
        try:
            return [self._tracks[uri]]
        except KeyError:
            logger.debug("track lookup cache miss %r", uri)
        try:
            _, _, identifier, _, filename = urisplit(uri)
            tracks = self._lookup(identifier)
            self._tracks = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        except Exception as e:
            logger.error('Lookup failed for %s: %s', uri, e)
            return []

    def browse(self, uri):
        try:
            identifier = urisplit(uri).path
            if not identifier:
                return self._browse_root()
            elif identifier in self._config['collections']:
                return self._browse_collection(identifier)
            else:
                return self._browse_item(identifier)
        except Exception as e:
            logger.error('Error browsing %s: %s', uri, e)
            return []

    def search(self, query=None, uris=None):
        try:
            terms = []
            for field, value in (query.iteritems() if query else []):
                if field not in _QUERY_MAPPING:
                    return None  # no result if unmapped field
                elif isinstance(value, basestring):
                    terms.append((_QUERY_MAPPING[field], value))
                else:
                    terms.extend((_QUERY_MAPPING[field], v) for v in value)
            if uris:
                ids = filter(None, (urisplit(uri).path for uri in uris))
                terms.append(('collection', tuple(ids)))
            return self._search(*terms)
        except Exception as e:
            logger.error('Error searching the Internet Archive: %s', e)
            return None

    def find_exact(self, query=None, uris=None):
        try:
            terms = []
            for field, value in (query.iteritems() if query else []):
                if field not in _QUERY_MAPPING:
                    return None  # no result if unmapped field
                elif isinstance(value, basestring):
                    terms.append((_QUERY_MAPPING[field], value))
                else:
                    terms.extend((_QUERY_MAPPING[field], v) for v in value)
            if uris:
                ids = filter(None, (urisplit(uri).path for uri in uris))
                terms.append(('collection', tuple(ids)))
            result = self._search(*terms)
            albums = filter(Query(query, True).match_album, result.albums)
            return result.copy(albums=albums)
        except Exception as e:
            logger.error('Error searching the Internet Archive: %s', e)
            return None

    def refresh(self, uri=None):
        logger.info('Clearing Internet Archive cache')
        self._cache.clear()
        self._tracks.clear()

    def get_stream_url(self, uri):
        _, _, identifier, _, filename = urisplit(uri)
        return self.backend.client.geturl(identifier, filename)

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_root(self):
        collections = self._config['collections']
        result = self.backend.client.search(
            _query(identifier=collections, mediatype='collection'),
            fields=['identifier', 'title', 'mediatype'],
            rows=len(collections)
        )
        # return in same order as listed in config
        docs = {doc['identifier']: doc for doc in result}
        refs = []
        for id in collections:
            if id in docs:
                refs.append(_ref(docs[id]))
            else:
                logger.warn('Internet Archive collection "%s" not found', id)
        return refs

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_collection(self, identifier):
        result = self.backend.client.search(
            _query(collection=identifier, **self._search_filter),
            fields=['identifier', 'title', 'mediatype'],
            sort=self._config['browse_order'],
            rows=self._config['browse_limit']
        )
        return map(_ref, result)

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_item(self, identifier):
        tracks = self._lookup(identifier)
        self._tracks = {t.uri: t for t in tracks}  # cache tracks
        return [Ref.track(uri=t.uri, name=t.name) for t in tracks]

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _lookup(self, identifier):
        client = self.backend.client
        item = client.metadata(identifier)
        # TODO: original vs. derived, "tmp" values?
        files = collections.defaultdict(list)
        for file in item['files']:
            files[file['format']].append(file)
        images = []
        for file in _getfirstitem(files, self._config['image_formats'], []):
            images.append(client.geturl(identifier, file['name']))
        album = _album(item['metadata'], images)
        tracks = []
        for file in _getfirstitem(files, self._config['audio_formats'], []):
            tracks.append(_track(item['metadata'], file, album))
        # sort tracks by track_no if given, by uri/filename otherwise
        tracks.sort(key=lambda t: (t.track_no or 0, t.uri))
        return tracks

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _search(self, *terms):
        result = self.backend.client.search(
            _query(*terms, **self._search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            sort=self._config['search_order'],
            rows=self._config['search_limit']
        )
        uri = uricompose(Extension.ext_name, query=result.query)
        return SearchResult(uri=uri, albums=[_album(doc) for doc in result])
