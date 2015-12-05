from __future__ import unicode_literals

import collections
import logging

from mopidy import backend, models

from . import Extension, translator

logger = logging.getLogger(__name__)


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = models.Ref.directory(
        uri=translator.uri(''), name='Internet Archive'
    )

    def __init__(self, config, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.__collections = config['collections']
        self.__audio_formats = config['audio_formats']
        self.__image_formats = config['image_formats']

        self.__browse_filter = '(mediatype:collection OR format:(%s))' % (
            ' OR '.join(map(translator.quote, config['audio_formats']))
        )
        self.__browse_limit = config['browse_limit']
        self.__browse_views = config['browse_views']

        self.__search_filter = 'format:(%s)' % (
            ' OR '.join(map(translator.quote, config['audio_formats']))
        )
        self.__search_limit = config['search_limit']
        self.__search_order = config['search_order']

        self.__directories = collections.OrderedDict()
        self.__lookup = {}  # track cache for faster lookup

    def browse(self, uri):
        identifier, filename, query = translator.parse_uri(uri)
        if filename:
            return []
        elif identifier and query:
            return self.__browse_collection(identifier, **query)
        elif identifier:
            return self.__browse_item(identifier)
        else:
            return self.__browse_root()

    def get_images(self, uris):
        # map uris to item identifiers
        urimap = collections.defaultdict(list)
        for uri in uris:
            identifier, _, _ = translator.parse_uri(uri)
            if identifier:
                urimap[identifier].append(uri)
            else:
                logger.debug('Not retrieving images for %s', uri)
        # retrieve item images and map back to uris
        results = {}
        for identifier, uris in urimap.items():
            try:
                item = self.backend.client.getitem(identifier)
            except Exception as e:
                logger.error('Error retrieving images for %s: %s', uris, e)
            else:
                results.update(dict.fromkeys(uris, self.__images(item)))
        return results

    def lookup(self, uri):
        try:
            return [self.__lookup[uri]]
        except KeyError:
            logger.debug("Lookup cache miss for %r", uri)
        identifier, filename, _ = translator.parse_uri(uri)
        if identifier:
            tracks = self.__tracks(self.backend.client.getitem(identifier))
            self.__lookup = trackmap = {t.uri: t for t in tracks}
            return [trackmap[uri]] if filename else tracks
        else:
            return []

    def refresh(self, uri=None):
        client = self.backend.client
        if client.cache:
            client.cache.clear()
        self.__directories.clear()
        self.__lookup.clear()

    def search(self, query=None, uris=None, exact=False):
        # sanitize uris
        uris = set(uris or [self.root_directory.uri])
        if self.root_directory.uri in uris:
            uris.update(map(translator.uri, self.__collections))
            uris.remove(self.root_directory.uri)
        # translate query
        try:
            qs = translator.query(query, uris, exact)
        except ValueError as e:
            logger.info('Not searching %s: %s', Extension.dist_name, e)
            return None
        else:
            logger.debug('Internet Archive query: %s' % qs)
        # fetch results
        result = self.backend.client.search(
            '%s AND %s' % (qs, self.__search_filter),
            fields=['identifier', 'title', 'creator', 'date'],
            rows=self.__search_limit,
            sort=self.__search_order
        )
        return models.SearchResult(
            uri=translator.uri(q=result.query),
            albums=map(translator.album, result)
        )

    def __browse_collection(self, identifier, sort=['downloads desc']):
        return list(map(translator.ref, self.backend.client.search(
            'collection:%s AND %s' % (identifier, self.__browse_filter),
            fields=['identifier', 'mediatype', 'title', 'creator'],
            rows=self.__browse_limit,
            sort=sort
        )))

    def __browse_item(self, identifier):
        if identifier in self.__directories:
            return self.__views(identifier)
        item = self.backend.client.getitem(identifier)
        if item['metadata']['mediatype'] == 'collection':
            return self.__views(identifier)
        tracks = self.__tracks(item)
        self.__lookup = {t.uri: t for t in tracks}  # cache tracks
        return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]

    def __browse_root(self):
        if not self.__directories:
            result = self.backend.client.search(
                'mediatype:collection AND identifier:(%s)' % (
                    ' OR '.join(self.__collections)
                ),
                fields=['identifier', 'mediatype', 'title']
            )
            objs = {obj['identifier']: obj for obj in result}
            for identifier in self.__collections:
                try:
                    obj = objs[identifier]
                except KeyError as e:
                    logger.warn('Internet Archive collection not found: %s', e)
                else:
                    self.__directories[identifier] = translator.ref(obj)
        return list(self.__directories.values())

    def __images(self, item):
        uri = self.backend.client.geturl  # get download URL for images
        return translator.images(item, self.__image_formats, uri)

    def __tracks(self, item, key=lambda t: (t.track_no or 0, t.uri)):
        tracks = translator.tracks(item, self.__audio_formats)
        tracks.sort(key=key)
        return tracks

    def __views(self, identifier):
        refs = []
        for order, name in self.__browse_views.items():
            uri = translator.uri(identifier, sort=order)
            refs.append(models.Ref.directory(name=name, uri=uri))
        return refs
