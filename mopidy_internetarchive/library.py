from __future__ import unicode_literals

import collections
import logging
import operator

import cachetools

from mopidy import backend, models

import uritools

from . import Extension, translator
from .query import Query

SCHEME = Extension.ext_name

QUERY_MAPPING = {
    'any': None,
    'album': 'title',
    'albumartist': 'creator',
    'date': 'date'
}

logger = logging.getLogger(__name__)


def _bookmarks(config):
    if not config['username']:
        return None
    uri = uritools.uricompose(
        scheme=SCHEME,
        userinfo=config['username'],
        host=uritools.urisplit(config['base_url']).host,
        path='/bookmarks/'
    )
    return models.Ref.directory(name='Archive Bookmarks', uri=uri)


def _cache(cache_size=None, cache_ttl=None, **kwargs):
    """Cache factory"""
    if cache_size is None:
        return None  # mainly for testing/debugging
    elif cache_ttl is None:
        return cachetools.LRUCache(cache_size)
    else:
        return cachetools.TTLCache(cache_size, cache_ttl)


def _trackkey(track):
    return (track.track_no or 0, track.uri)


def _find(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = models.Ref.directory(
        uri=uritools.uricompose(SCHEME),
        name='Internet Archive'
    )

    def __init__(self, config, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self._config = ext_config = config[Extension.ext_name]
        self._search_filter = {
            'format': ext_config['audio_formats'],
            '-collection': ext_config['exclude_collections'],
            '-mediatype': ext_config['exclude_mediatypes']
        }
        self._bookmarks = _bookmarks(ext_config)
        self._cache = _cache(**ext_config)
        self._tracks = {}  # track cache for faster lookup

    def lookup(self, uri):
        try:
            return [self._tracks[uri]]
        except KeyError:
            logger.debug("track lookup cache miss %r", uri)
        try:
            _, _, identifier, _, filename = uritools.urisplit(uri)
            tracks = self._lookup(identifier)
            self._tracks = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        except Exception as e:
            logger.error('Lookup failed for %s: %s', uri, e)
            return []

    def browse(self, uri):
        logger.info('browse %r', uri)
        try:
            parts = uritools.urisplit(uri)
            if not parts.path:
                return self._browse_root()
            elif parts.userinfo:
                return self._browse_bookmarks(parts.userinfo)
            elif parts.path in self._config['collections']:
                return self._browse_collection(parts.path)
            else:
                return self._browse_item(parts.path)
        except Exception as e:
            logger.error('Error browsing %s: %s', uri, e)
            return []

    def search(self, query=None, uris=None, exact=False):
        if exact:
            return self.find_exact(query, uris)
        try:
            terms = []
            for field, values in (query.iteritems() if query else []):
                if field not in QUERY_MAPPING:
                    return None  # no result if unmapped field
                else:
                    terms.extend((QUERY_MAPPING[field], v) for v in values)
            if uris:
                urisplit = uritools.urisplit
                ids = filter(None, (urisplit(uri).path for uri in uris))
                terms.append(('collection', tuple(ids)))
            return self._search(*terms)
        except Exception as e:
            logger.error('Error searching the Internet Archive: %s', e)
            return None

    def find_exact(self, query=None, uris=None):
        try:
            terms = []
            for field, values in (query.iteritems() if query else []):
                if field not in QUERY_MAPPING:
                    return None  # no result if unmapped field
                else:
                    terms.extend((QUERY_MAPPING[field], v) for v in values)
            if uris:
                urisplit = uritools.urisplit
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

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_root(self):
        logger.info('browse root')
        collections = self._config['collections']
        refs = [self._bookmarks] if self._bookmarks else []
        docs = {doc['identifier']: doc for doc in self.backend.client.search(
            translator.query(identifier=collections, mediatype='collection'),
            fields=['identifier', 'title', 'mediatype'],
            rows=len(collections)
        )}
        # return in same order as listed in config
        for id in collections:
            if id in docs:
                refs.append(translator.ref(docs[id]))
            else:
                logger.warn('Internet Archive collection "%s" not found', id)
        return refs

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_bookmarks(self, username):
        return map(translator.ref, self.backend.client.bookmarks(username))

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_collection(self, identifier):
        return map(translator.ref, self.backend.client.search(
            translator.query(collection=identifier, **self._search_filter),
            fields=['identifier', 'title', 'mediatype'],
            sort=self._config['browse_order'],
            rows=self._config['browse_limit']
        ))

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _browse_item(self, identifier):
        tracks = self._lookup(identifier)
        self._tracks = {t.uri: t for t in tracks}  # cache tracks
        return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _lookup(self, identifier):
        client = self.backend.client
        item = client.metadata(identifier)
        files = collections.defaultdict(dict)
        # HACK: not all files have "mtime", but reverse-sorting on
        # filename tends to preserve "l(e)ast derived" versions,
        # e.g. "filename.mp3" over "filename_vbr.mp3"
        key = operator.itemgetter('name')
        for file in sorted(item['files'], key=key, reverse=True):
            original = str(file.get('original', file['name']))
            files[file['format']][original] = file
        images = []
        for file in _find(files, self._config['image_formats'], {}).values():
            images.append(client.geturl(identifier, file['name']))
        album = translator.album(item['metadata'], images)
        tracks = []
        for file in _find(files, self._config['audio_formats'], {}).values():
            tracks.append(translator.track(item['metadata'], file, album))
        tracks.sort(key=_trackkey)
        return tracks

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def _search(self, *terms):
        result = self.backend.client.search(
            translator.query(*terms, **self._search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            sort=self._config['search_order'],
            rows=self._config['search_limit']
        )
        uri = uritools.uricompose(SCHEME, query=result.query)
        albums = [translator.album(doc) for doc in result]
        return models.SearchResult(uri=uri, albums=albums)
