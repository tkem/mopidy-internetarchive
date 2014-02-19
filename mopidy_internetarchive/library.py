from __future__ import unicode_literals

import collections
import logging

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .query import Query
from .translators import doc_to_album, item_to_tracks
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    BROWSE_FIELDS = ('identifier', 'title', 'mediatype'),

    SEARCH_FIELDS = ('identifier', 'title', 'creator', 'date', 'publicdate')

    def __init__(self, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.root_directory = Ref.directory(
            uri=uricompose(backend.SCHEME, path='/'),
            name=self.config['browse_label']
        )

        collections = {}
        for identifier in self.config['collections']:
            try:
                item = self.backend.client.metadata(identifier + '/metadata')
            except Exception as e:
                # TODO: handle temporary error (network connection, etc.)
                logger.error('Error loading item %s: %s', identifier, e)
                continue
            if item['mediatype'] == 'collection':
                ref = self._docref(item)
                collections[ref.uri] = ref
            else:
                logger.error('Item %r not a collection' % identifier)
        logger.info("Loaded %d Internet Archive collections", len(collections))
        self.collections = collections

        bookmarks = {}
        for username in self.config['bookmarks']:
            # TODO: prettier bookmarks URI, check for existence
            uri = uricompose(self.backend.SCHEME, authority=(username + '@'))
            name = self.config['bookmarks_label'].format(username)
            bookmarks[uri] = Ref.directory(uri=uri, name=name)
        logger.info("Loaded %d Internet Archive bookmarks", len(bookmarks))
        self.bookmarks = bookmarks

    @property
    def config(self):
        return self.backend.config[self.backend.SCHEME]

    def browse(self, uri):
        logger.debug("internetarchive browse %r", uri)

        try:
            if not uri:
                return [self.root_directory]
            elif uri == self.root_directory.uri:
                return self.collections.values() + self.bookmarks.values()
            elif uri in self.collections:
                return self._browse_collection(urisplit(uri).path)
            elif uri in self.bookmarks:
                return self._browse_bookmarks(urisplit(uri).userinfo)
            else:
                return self._browse_item(urisplit(uri).path)
        except Exception as error:
            logger.error('internetarchive browse %s: %s', uri, error)
            return []

    def lookup(self, uri):
        logger.debug("internetarchive lookup %r", uri)

        try:
            _, _, identifier, _, filename = urisplit(uri)
            item = self.backend.client.metadata(identifier)
            if filename:
                files = [f for f in item['files'] if f['name'] == filename]
            else:
                files = self._files_by_format(item['files'])
            logger.debug("internetarchive files: %r", files)
            return item_to_tracks(item, files)
        except Exception as error:
            logger.error('internetarchive lookup %s: %s', uri, error)
            return []

    def find_exact(self, query=None, uris=None):
        logger.debug("internetarchive find %r", query)

        if not query:
            return
        try:
            return SearchResult(
                uri=uricompose(self.backend.SCHEME, query=''),
                albums=self._find_albums(Query(query, True))
            )
        except Exception as error:
            logger.error('internetarchive find %r: %s', query, error)
            return None

    def search(self, query=None, uris=None):
        logger.debug("internetarchive search %r", query)

        if not query:
            return
        try:
            return SearchResult(
                uri=uricompose(self.backend.SCHEME, query=''),
                albums=self._find_albums(Query(query, False))
            )
        except Exception as error:
            logger.error('internetarchive search %r: %s', query, error)
            return None

    def get_stream_url(self, uri):
        _, _, identifier, _, filename = urisplit(uri)
        return self.backend.client.geturl(identifier.lstrip('/'), filename)

    def _find_albums(self, query):
        terms = {}
        for (field, values) in query.iteritems():
            if field == "any":
                terms[None] = values
            elif field == "album":
                terms['title'] = values
            elif field == "artist":
                terms['creator'] = values
            elif field == 'date':
                terms['date'] = values
        qs = self.backend.client.query_string(terms)

        result = self.backend.client.search(
            qs + ' AND ' + self.backend.client.query_string({
                'collection': self.config['collections'],
                'mediatype':  self.config['mediatypes'],
                'format': self.config['formats']
            }, group_op='OR'),
            fields=self.SEARCH_FIELDS,
            sort=self.config['sort_order'],
            rows=self.config['search_limit']
        )
        albums = [doc_to_album(doc) for doc in result]
        logger.debug("internetarchive found albums: %r", albums)
        return query.filter_albums(albums)

    def _browse_collection(self, identifier):
        result = self.backend.client.search(
            self.backend.client.query_string({
                'collection': identifier,
                'mediatype': self.config['mediatypes'],
                'format': self.config['formats']
            }, group_op='OR'),
            fields=self.BROWSE_FIELDS,
            sort=self.config['sort_order'],
            rows=self.config['browse_limit']
        )
        return [self._docref(doc) for doc in result]

    def _browse_bookmarks(self, username):
        result = self.backend.client.bookmarks(username)
        return [self._docref(doc) for doc in result]

    def _browse_item(self, identifier):
        item = self.backend.client.metadata(identifier)
        if item['metadata']['mediatype'] not in self.config['mediatypes']:
            return []
        refs = []
        scheme = self.backend.SCHEME
        for f in self._files_by_format(item['files']):
            uri = uricompose(scheme, path=identifier, fragment=f['name'])
            # TODO: title w/slash or 'tmp'
            name = f.get('title', f['name'])
            refs.append(Ref.track(uri=uri, name=name))
        return refs

    def _docref(self, doc):
        identifier = doc['identifier']
        uri = uricompose(self.backend.SCHEME, path=identifier)
        # TODO: title w/slash
        name = doc.get('title', identifier)
        return Ref.directory(uri=uri, name=name)

    def _files_by_format(self, files):
        byformat = collections.defaultdict(list)
        for f in files:
            byformat[f['format'].lower()].append(f)
        for fmt in [fmt.lower() for fmt in self.config['formats']]:
            if fmt in byformat:
                return byformat[fmt]
            for key in byformat.keys():
                if fmt in key:
                    return byformat[key]
        return []
