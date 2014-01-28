from __future__ import unicode_literals

import logging

from collections import defaultdict

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .translators import item_to_tracks, metadata_to_album
from .translators import metadata_to_ref, file_to_ref
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)

URI_SCHEMA = 'internetarchive'

SEARCH_FIELDS = ['identifier', 'title', 'creator', 'date', 'publicdate']


def _filter_by_name(files, name):
    for f in files:
        if f['name'] == name:
            return [f]
    return []


def _filter_by_format(files, formats):
    byformat = defaultdict(list)
    for f in files:
        byformat[f['format'].lower()].append(f)
    for fmt in formats:
        if fmt in byformat:
            return byformat[fmt]
        for k in byformat.keys():
            if k.endswith(fmt):
                return byformat[k]
    return []


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(
        uri='internetarchive:',
        name='Internet Archive')

    def __init__(self, backend, config):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.config = config
        self.formats = [fmt.lower() for fmt in config['formats']]

    def browse(self, uri):
        logger.debug("internetarchive browse: %s", uri)

        if not uri:
            return [self.root_directory]

        uriparts = urisplit(uri)

        if uri == self.root_directory.uri:
            result = self.backend.client.search(
                'mediatype:collection AND collection:etree',
                fields=['identifier', 'title', 'mediatype'],
                sort=['downloads desc'],
                rows=self.config['browse_limit'])
            return [metadata_to_ref(d, Ref.DIRECTORY) for d in result.docs]

        item = self.backend.client.getitem(uriparts.path)
        if item['metadata']['mediatype'] == 'collection':
            result = self.backend.client.search(
                'mediatype:etree AND collection:%s' % uriparts.path,
                fields=['identifier', 'title', 'mediatype'],
                rows=self.config['browse_limit'])
            return [metadata_to_ref(d, Ref.DIRECTORY) for d in result.docs]
        elif item['metadata']['mediatype'] == 'etree':
            files = _filter_by_format(item['files'], self.formats)
            logger.debug("got files: %s", repr(files))
            return [file_to_ref(item, f) for f in files]
        else:
            return []

    def lookup(self, uri):
        logger.debug("internetarchive lookup: %s", uri)

        try:
            uriparts = urisplit(uri)
            item = self.backend.client.getitem(uriparts.path)
            if uriparts.fragment:
                files = _filter_by_name(item['files'], uriparts.fragment)
            else:
                files = _filter_by_format(item['files'], self.formats)
            return item_to_tracks(item, files)
        except Exception as error:
            logger.error('Failed to lookup %s: %s', uri, error)
            return []

    def search(self, query=None, uris=None):
        logger.debug("internetarchive search: %s", repr(query))

        if not query:
            return
        result = self.backend.client.search(
            self._query_to_string(query),
            fields=SEARCH_FIELDS,
            rows=self.config['search_limit'])
        albums = [metadata_to_album(doc) for doc in result.docs]
        return SearchResult(
            uri=uricompose(URI_SCHEMA, query=result.query),
            albums=albums)

    def _query_to_string(self, query):
        terms = []
        for (field, value) in query.iteritems():
            # TODO: better quote/range handling
            if field == "any":
                terms.append(self._query_value_to_string(value))
            elif field == "album":
                terms.append('title:' + self._query_value_to_string(value))
            elif field == "artist":
                terms.append('creator:' + self._query_value_to_string(value))
            elif field == 'date':
                terms.append('date:' + value[0])
            # TODO: other fields as filter
        terms.append('collection:(' +
                     ' OR '.join(self.config['collections']) + ')')
        terms.append('mediatype:(' +
                     ' OR '.join(self.config['mediatypes']) + ')')
        terms.append('format:(' +
                     ' OR '.join(self.config['formats']) + ')')
        return ' '.join(terms)

    def _query_value_to_string(self, value):
        if hasattr(value, '__iter__'):
            return '(' + ' OR '.join(value) + ')'
        else:
            return value
