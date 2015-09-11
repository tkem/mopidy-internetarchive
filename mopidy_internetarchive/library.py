from __future__ import unicode_literals

import collections
import itertools
import logging
import operator
import re

from mopidy import backend, models

import uritools

from . import Extension, translator

QUERY_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')

QUERY_MAPPING = {
    'any': None,
    'album': 'title',
    'albumartist': 'creator',
    'date': 'date'
}

SCHEME = Extension.ext_name

logger = logging.getLogger(__name__)


def _find(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


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


def _quote(term):
    term = QUERY_CHAR_RE.sub(r'\\\1', term)
    # only quote if term contains whitespace, since date:"2014-01-01"
    # will raise an error
    if any(c.isspace() for c in term):
        term = '"' + term + '"'
    return term


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
        # TODO: remove bookmarks, treat as normal collection
        if ext_config['username']:
            self.__bookmarks = models.Ref.directory(
                name='Archive Bookmarks',
                uri=uritools.uricompose(
                    scheme=SCHEME,
                    userinfo=ext_config['username'],
                    host=uritools.urisplit(ext_config['base_url']).host,
                    path='/bookmarks/'
                )
            )
        else:
            self.__bookmarks = None
        self.__tracks = {}  # track cache for faster lookup

    def browse(self, uri):
        parts = uritools.urisplit(uri)
        if not parts.path:
            return self.__browse_root()
        elif parts.userinfo:
            return self.__browse_bookmarks(parts.userinfo)
        elif parts.path in self.__config['collections']:
            return self.__browse_collection(parts.path)
        else:
            return self.__browse_item(parts.path)

    def lookup(self, uri):
        try:
            return [self.__tracks[uri]]
        except KeyError:
            logger.debug("track lookup cache miss for %r", uri)
        try:
            _, _, identifier, _, filename = uritools.urisplit(uri)
            tracks = self.__lookup(identifier)
            self.__tracks = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        except Exception as e:
            logger.error('Lookup failed for %s: %s', uri, e)
            return []

    def refresh(self, uri=None):
        if self.backend.client.cache:
            self.backend.client.cache.clear()
        self.__tracks.clear()

    def search(self, query=None, uris=None, exact=False):
        if exact:
            return None  # exact queries not supported
        terms = []
        for field, values in (query.iteritems() if query else []):
            if field not in QUERY_MAPPING:
                return None  # no result if unmapped field
            else:
                terms.extend((QUERY_MAPPING[field], v) for v in values)
        if uris:
            ids = filter(None, [uritools.urisplit(uri).path for uri in uris])
            terms.append(('collection', tuple(ids)))
        result = self.backend.client.search(
            _query(*terms, **self.__search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            sort=self.__config['search_order'],
            rows=self.__config['search_limit']
        )
        return models.SearchResult(
            uri=uritools.uricompose(SCHEME, query=result.query),
            albums=map(translator.album, result)
        )

    def __browse_root(self):
        collections = self.__config['collections']
        refs = [self.__bookmarks] if self.__bookmarks else []
        objs = {obj['identifier']: obj for obj in self.backend.client.search(
            _query(identifier=collections, mediatype='collection'),
            fields=['identifier', 'title', 'mediatype', 'creator'],
            rows=len(collections)
        )}
        # return in same order as listed in config
        for id in collections:
            if id in objs:
                refs.append(translator.ref(objs[id]))
            else:
                logger.warn('Internet Archive collection "%s" not found', id)
        return refs

    def __browse_bookmarks(self, username):
        return map(translator.ref, self.backend.client.bookmarks(username))

    def __browse_collection(self, identifier):
        return map(translator.ref, self.backend.client.search(
            _query(collection=identifier, **self.__search_filter),
            fields=['identifier', 'title', 'mediatype', 'creator'],
            sort=self.__config['browse_order'],
            rows=self.__config['browse_limit']
        ))

    def __browse_item(self, identifier):
        tracks = self.__lookup(identifier)
        self.__tracks = {t.uri: t for t in tracks}  # cache tracks
        return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]

    def __lookup(self, identifier):
        client = self.backend.client
        files = collections.defaultdict(dict)
        item = client.getitem(identifier)
        # HACK: not all files have "mtime", but reverse-sorting on
        # filename tends to preserve "l(e)ast derived" versions,
        # e.g. "filename.mp3" over "filename_vbr.mp3"
        key = operator.itemgetter('name')
        for file in sorted(item['files'], key=key, reverse=True):
            original = str(file.get('original', file['name']))
            files[file['format']][original] = file
        images = []
        for file in _find(files, self.__config['image_formats'], {}).values():
            images.append(client.geturl(identifier, file['name']))
        album = translator.album(item['metadata'], images)
        tracks = []
        for file in _find(files, self.__config['audio_formats'], {}).values():
            tracks.append(translator.track(item['metadata'], file, album))
        tracks.sort(key=lambda t: (t.track_no or 0, t.uri))
        return tracks
