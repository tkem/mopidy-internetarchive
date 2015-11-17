from __future__ import unicode_literals

import collections
import logging
import operator

from mopidy import backend, models

import uritools

from . import Extension, translator

logger = logging.getLogger(__name__)


def _find(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = models.Ref.directory(
        uri=uritools.uricompose(Extension.ext_name),
        name='Internet Archive'
    )

    def __init__(self, config, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.__config = ext_config = config[Extension.ext_name]
        self.__browse_filter = '(mediatype:collection OR format:(%s))' % (
            ' OR '.join(map(translator.quote, ext_config['audio_formats']))
        )
        self.__search_filter = 'format:(%s)' % (
            ' OR '.join(map(translator.quote, ext_config['audio_formats']))
        )
        self.__lookup = {}  # track cache for faster lookup

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
            return [self.__lookup[uri]]
        except KeyError:
            logger.debug("Lookup cache miss for %r", uri)
        try:
            _, _, identifier, _, filename = uritools.urisplit(uri)
            tracks = self.__tracks(self.backend.client.getitem(identifier))
            self.__lookup = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        except Exception as e:
            logger.error('Lookup failed for %s: %s', uri, e)
            return []

    def refresh(self, uri=None):
        if self.backend.client.cache:
            self.backend.client.cache.clear()
        self.__lookup.clear()

    def search(self, query=None, uris=None, exact=False):
        # sanitize uris
        uris = set(uris or [self.root_directory.uri])
        if self.root_directory.uri in uris:
            # TODO: from cached root collections?
            uris.update(translator.uri(identifier)
                        for identifier in self.__config['collections'])
            uris.remove(self.root_directory.uri)
        try:
            qs = translator.query(query, uris, exact)
        except ValueError as e:
            logger.info('Not searching %s: %s', Extension.dist_name, e)
            return None
        else:
            logger.debug('Internet Archive query: %s' % qs)
        result = self.backend.client.search(
            '%s AND %s' % (qs, self.__search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            rows=self.__config['search_limit'],
            sort=self.__config['search_order']
        )
        return models.SearchResult(
            uri=uritools.uricompose(Extension.ext_name, query=result.query),
            albums=map(translator.album, result)
        )

    def __browse_collection(self, identifier, q=[], sort=['downloads desc']):
        if identifier:
            qs = 'collection:%s' % identifier
        else:
            qs = ' AND '.join(q)
        return list(map(translator.ref, self.backend.client.search(
            '%s AND %s' % (qs, self.__browse_filter),
            fields=['identifier', 'title', 'mediatype', 'creator'],
            rows=self.__config['browse_limit'],
            sort=sort
        )))

    def __browse_item(self, item):
        metadata = item['metadata']
        if metadata.get('mediatype') != 'collection':
            tracks = self.__tracks(item)
            self.__lookup = {t.uri: t for t in tracks}  # cache tracks
            return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]
        elif 'members' in item:
            return list(map(translator.ref, item['members']))
        else:
            return self.__browse_views(metadata['identifier'])

    def __browse_views(self, identifier, scheme=Extension.ext_name):
        refs = []
        for order, name in self.__config['browse_views'].items():
            uri = uritools.uricompose(scheme, path=identifier, query={
                'sort': order
            })
            refs.append(models.Ref.directory(name=name, uri=uri))
        return refs

    def __browse_root(self):
        # TODO: cache this
        result = self.backend.client.search(
            'mediatype:collection AND identifier:(%s)' % (
                ' OR '.join(self.__config['collections'])
            ),
            fields=['identifier', 'title', 'mediatype', 'creator']
        )
        refs = []
        objs = {obj['identifier']: obj for obj in result}
        for identifier in self.__config['collections']:
            try:
                obj = objs[identifier]
            except KeyError:
                logger.warn('Internet Archive collection "%s" not found',
                            identifier)
            else:
                refs.append(translator.ref(obj))
        return refs

    def __tracks(self, item, namegetter=operator.itemgetter('name')):
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
