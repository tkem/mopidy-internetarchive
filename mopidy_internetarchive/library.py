from __future__ import unicode_literals

import logging

from collections import defaultdict

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
            uri=uricompose(backend.URI_SCHEME, path='/'),
            name=self.getconfig('browse_label')
        )
        # fetch/cache top-level browse collections
        refs = self.browse(self.root_directory.uri)
        logger.info("Loaded %d Internet Archive collections", len(refs))

    def browse(self, uri):
        logger.debug("internetarchive browse: %s", uri)

        try:
            if not uri:
                return [self.root_directory]
            if uri == self.root_directory.uri:
                return self._browse_root()
            item = self.backend.client.getitem(urisplit(uri).path)
            if item['metadata']['mediatype'] == 'collection':
                return self._browse_collection(item['metadata']['identifier'])
            elif item['metadata']['mediatype'] in self.getconfig('mediatypes'):
                return self._browse_item(item)
            else:
                return []
        except Exception as error:
            logger.error('internetarchive browse %s: %s', uri, error)
            return []

    def lookup(self, uri):
        logger.debug("internetarchive lookup: %s", uri)

        try:
            _, _, identifier, _, filename = urisplit(uri)
            item = self.backend.client.getitem(identifier)
            if filename:
                files = [f for f in item['files'] if f['name'] == filename]
            else:
                files = self._byformat(item['files'])
            logger.debug("internetarchive files: %r", files)
            return item_to_tracks(item, files)
        except Exception as error:
            logger.error('internetarchive lookup %s: %s', uri, error)
            return []

    def find_exact(self, query=None, uris=None):
        logger.debug("internetarchive find exact: %r", query)
        return self._find(Query(query, True)) if query else None

    def search(self, query=None, uris=None):
        logger.debug("internetarchive search: %r", query)
        return self._find(Query(query, False)) if query else None

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def getstream(self, uri):
        _, _, identifier, _, filename = urisplit(uri)
        return self.backend.client.geturl(identifier, filename)

    def _find(self, query):
        terms = {
            'collection': self.getconfig('collections'),
            'mediatype':  self.getconfig('mediatypes'),
            'format': self.getconfig('formats')
        }
        for (field, values) in query.iteritems():
            if field == "any":
                terms[None] = values
            elif field == "album":
                terms['title'] = values
            elif field == "artist":
                terms['creator'] = values
            elif field == 'date':
                terms['date'] = values
        result = self.backend.client.search(
            query=self.backend.client.query_string(terms),
            fields=self.SEARCH_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('search_limit'))
        albums = [doc_to_album(doc) for doc in result.docs]
        logger.debug("internetarchive albums: %r", albums)

        return SearchResult(
            uri=uricompose(self.backend.URI_SCHEME, query=result.query),
            albums=query.filter_albums(albums)
        )

    def _browse_root(self):
        result = self.backend.client.search(
            query=self.backend.client.query_string({
                'mediatype': 'collection',
                'identifier': self.getconfig('collections')
            }),
            fields=self.BROWSE_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('browse_limit'))
        return [self._doc_ref(doc) for doc in result.docs]

    def _browse_collection(self, identifier):
        result = self.backend.client.search(
            query=self.backend.client.query_string({
                'collection': identifier,
                'mediatype': self.getconfig('mediatypes'),
                'format': self.getconfig('formats')
            }),
            fields=self.BROWSE_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('browse_limit'))
        return [self._doc_ref(doc) for doc in result.docs]

    def _browse_item(self, item):
        files = self._byformat(item['files'])
        return [self._file_ref(item, f) for f in files]

    def _doc_ref(self, doc):
        identifier = doc['identifier']
        uri = uricompose(self.backend.URI_SCHEME, path=identifier)
        # TODO: title w/slash
        name = doc.get('title', identifier)
        return Ref.directory(uri=uri, name=name)

    def _file_ref(self, item, file):
        uri = uricompose(
            self.backend.URI_SCHEME,
            path=item['metadata']['identifier'],
            fragment=file['name']
        )
        # TODO: title w/slash or 'tmp'
        name = file.get('title', file['name'])
        return Ref.track(uri=uri, name=name)

    def _byformat(self, files):
        byformat = defaultdict(list)
        for f in files:
            byformat[f['format'].lower()].append(f)
        for fmt in [fmt.lower() for fmt in self.getconfig('formats')]:
            if fmt in byformat:
                return byformat[fmt]
            for key in byformat.keys():
                if fmt in key:
                    return byformat[key]
        return []
