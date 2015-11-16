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


def _trackref(track):
    return models.Ref.track(name=track.name, uri=track.uri)


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = models.Ref.directory(
        uri=uritools.uricompose(Extension.ext_name),
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
        self.__tracks = {}  # track cache for faster lookup

    def browse(self, uri):
        parts = uritools.urisplit(uri)
        if parts.query:
            return self.__browse_collection(parts.path, **parts.getquerydict())
        elif parts.path:
            return self.__browse_item(self.backend.client.getitem(parts.path))
        else:
            return self.__browse_root()

    def lookup(self, uri):
        try:
            return [self.__tracks[uri]]
        except KeyError:
            logger.debug("track lookup cache miss for %r", uri)
        try:
            _, _, identifier, _, filename = uritools.urisplit(uri)
            tracks = self.__gettracks(self.backend.client.getitem(identifier))
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
            uri=uritools.uricompose(Extension.ext_name, query=result.query),
            albums=map(translator.album, result)
        )

    def __browse_collection(self, identifier, q=[], sort=['downloads desc']):
        if identifier:
            query = _query(collection=identifier, **self.__search_filter),
        else:
            query = ' AND '.join(q) + ' AND ' + _query(**self.__search_filter)
        return map(translator.ref, self.backend.client.search(
            query,
            fields=['identifier', 'title', 'mediatype', 'creator'],
            rows=self.__config['browse_limit'],
            sort=sort
        ))

    def __browse_item(self, item):
        metadata = item['metadata']
        if metadata.get('mediatype') != 'collection':
            return list(map(_trackref, self.__gettracks(item)))
        elif 'members' in item:
            return list(map(translator.ref, item['members']))
        else:
            return self.__browse_views(metadata['identifier'])

        # tracks = self.__lookup(identifier)
        # self.__tracks = {t.uri: t for t in tracks}  # cache tracks
        # return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]

    def __browse_views(self, identifier, scheme=Extension.ext_name):
        refs = []
        for order, name in self.__config['browse_views'].items():
            uri = uritools.uricompose(scheme, path=identifier, query={
                'sort': order
            })
            refs.append(models.Ref.directory(name=name, uri=uri))
        return refs

    def __browse_root(self):
        collections = self.__config['collections']
        objs = {obj['identifier']: obj for obj in self.backend.client.search(
            _query(identifier=collections, mediatype='collection'),
            fields=['identifier', 'title', 'mediatype', 'creator'],
            rows=len(collections)
        )}
        # keep order from config
        refs = []
        for identifier in collections:
            try:
                obj = objs[identifier]
            except KeyError:
                logger.warn('Internet Archive collection "%s" not found',
                            identifier)
            else:
                refs.append(translator.ref(obj))
        return refs

    def __gettracks(self, item, namegetter=operator.itemgetter('name')):
        client = self.backend.client
        metadata = item['metadata']
        files = collections.defaultdict(dict)
        # HACK: not all files have "mtime", but reverse-sorting on
        # filename tends to preserve "l(e)ast derived" versions,
        # e.g. "filename.mp3" over "filename_vbr.mp3"
        for file in sorted(item['files'], key=namegetter, reverse=True):
            original = str(file.get('original', file['name']))
            files[file['format']][original] = file
        images = []
        for file in _find(files, self.__config['image_formats'], {}).values():
            images.append(client.geturl(metadata['identifier'], file['name']))
        album = translator.album(metadata, images)
        tracks = []
        for file in _find(files, self.__config['audio_formats'], {}).values():
            tracks.append(translator.track(metadata, file, album))
        tracks.sort(key=lambda t: (t.track_no or 0, t.uri))
        return tracks
