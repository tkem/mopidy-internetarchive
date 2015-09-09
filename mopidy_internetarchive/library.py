from __future__ import unicode_literals

import collections
import logging
import operator

import cachetools

from mopidy import backend, models

import uritools

from . import Extension, translator

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
        self.__config = ext_config = config[Extension.ext_name]
        self.__search_filter = {
            'format': ext_config['audio_formats'],
            '-collection': ext_config['exclude_collections'],
            '-mediatype': ext_config['exclude_mediatypes']
        }
        self.__bookmarks = _bookmarks(ext_config)
        self.__cache = _cache(**ext_config)
        self.__tracks = {}  # track cache for faster lookup

    def browse(self, uri):
        try:
            parts = uritools.urisplit(uri)
            if not parts.path:
                return self.__browse_root()
            elif parts.userinfo:
                return self.__browse_bookmarks(parts.userinfo)
            elif parts.path in self.__config['collections']:
                return self.__browse_collection(parts.path)
            else:
                return self.__browse_item(parts.path)
        except Exception as e:
            logger.error('Error browsing %s: %s', uri, e)
            return []

    def lookup(self, uri):
        try:
            return [self.__tracks[uri]]
        except KeyError:
            logger.debug("track lookup cache miss %r", uri)
        try:
            _, _, identifier, _, filename = uritools.urisplit(uri)
            tracks = self.__lookup(identifier)
            self.__tracks = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        except Exception as e:
            logger.error('Lookup failed for %s: %s', uri, e)
            return []

    def refresh(self, uri=None):
        self.__cache.clear()
        self.__tracks.clear()

    def search(self, query=None, uris=None, exact=False):
        if exact:
            return None  # exact queries not supported
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
            return self.__search(*terms)
        except Exception as e:
            logger.error('Error searching the Internet Archive: %s', e)
            return None

    def __browse_root(self):
        collections = self.__config['collections']
        refs = [self.__bookmarks] if self.__bookmarks else []
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

    def __browse_bookmarks(self, username):
        return map(translator.ref, self.backend.client.bookmarks(username))

    def __browse_collection(self, identifier):
        return map(translator.ref, self.backend.client.search(
            translator.query(collection=identifier, **self.__search_filter),
            fields=['identifier', 'title', 'mediatype'],
            sort=self.__config['browse_order'],
            rows=self.__config['browse_limit']
        ))

    def __browse_item(self, identifier):
        tracks = self.__lookup(identifier)
        self.__tracks = {t.uri: t for t in tracks}  # cache tracks
        return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]

    def __lookup(self, identifier):
        item = self.__getitem(identifier)
        files = collections.defaultdict(dict)
        # HACK: not all files have "mtime", but reverse-sorting on
        # filename tends to preserve "l(e)ast derived" versions,
        # e.g. "filename.mp3" over "filename_vbr.mp3"
        key = operator.itemgetter('name')
        for file in sorted(item['files'], key=key, reverse=True):
            original = str(file.get('original', file['name']))
            files[file['format']][original] = file
        images = []
        for file in _find(files, self.__config['image_formats'], {}).values():
            images.append(self.backend.client.geturl(identifier, file['name']))
        album = translator.album(item['metadata'], images)
        tracks = []
        for file in _find(files, self.__config['audio_formats'], {}).values():
            tracks.append(translator.track(item['metadata'], file, album))
        tracks.sort(key=_trackkey)
        return tracks

    def __search(self, *terms):
        result = self.backend.client.search(
            translator.query(*terms, **self.__search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            sort=self.__config['search_order'],
            rows=self.__config['search_limit']
        )
        uri = uritools.uricompose(SCHEME, query=result.query)
        albums = [translator.album(doc) for doc in result]
        return models.SearchResult(uri=uri, albums=albums)

    @cachetools.cachedmethod(lambda self: self.__cache)
    def __getitem(self, identifier):
        return self.backend.client.metadata(identifier)
