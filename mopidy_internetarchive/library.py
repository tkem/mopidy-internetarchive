from __future__ import unicode_literals

import logging

from collections import defaultdict

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .translators import item_to_tracks, metadata_to_album
from .translators import metadata_to_ref, file_to_ref
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)


def _query_term(field, values):
    if not hasattr(values, '__iter__'):
        values = [values]
    value = '(%s)' % ' OR '.join(values) if len(values) > 1 else values[0]
    if field:
        return '%s:%s' % (field, value)
    else:
        return value


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

    BROWSE_FIELDS = ('identifier', 'title', 'mediatype'),

    SEARCH_FIELDS = ('identifier', 'title', 'creator', 'date', 'publicdate')

    def __init__(self, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.root_directory = Ref.directory(
            uri='%s:/' % backend.URI_SCHEME,
            name=self.getconfig('browse_label'))
        self.formats = [fmt.lower() for fmt in self.getconfig('formats')]

    def browse(self, uri):
        logger.debug("internetarchive browse: %s", uri)

        if not uri:
            return [self.root_directory]

        if uri == self.root_directory.uri:
            result = self.backend.client.search(
                query='mediatype:collection' +
                ' AND collection:(' + ' OR '.join(self.getconfig('collections')) + ')',
                fields=self.BROWSE_FIELDS,
                sort=self.getconfig('sort_order'),
                rows=self.getconfig('browse_limit'))
            return [metadata_to_ref(d, Ref.DIRECTORY) for d in result.docs]

        uriparts = urisplit(uri)
        item = self.backend.client.getitem(uriparts.path)

        if item['metadata']['mediatype'] == 'collection':
            result = self.backend.client.search(
                query='collection:' + uriparts.path.strip('/') +
                ' AND mediatype:(' + ' OR '.join(self.getconfig('mediatypes')) + ')' +
                ' AND format:(' + ' OR '.join(self.getconfig('formats')) + ')',
                fields=self.BROWSE_FIELDS,
                sort=self.getconfig('sort_order'),
                rows=self.getconfig('browse_limit'))
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
            fields=self.SEARCH_FIELDS,
            rows=self.getconfig('search_limit'))
        albums = [metadata_to_album(doc) for doc in result.docs]
        return SearchResult(
            uri=uricompose(self.backend.URI_SCHEME, query=result.query),
            albums=albums)

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def _query_to_string(self, query):
        terms = [
            _query_term('collection', self.getconfig('collections')),
            _query_term('mediatype', self.getconfig('mediatypes')),
            _query_term('format', self.getconfig('formats'))
        ]
        for (field, value) in query.iteritems():
            # TODO: better quote/range handling
            if field == "any":
                terms.append(_query_term(None, value))
            elif field == "album":
                terms.append(_query_term('title', value))
            elif field == "artist":
                terms.append(_query_term('creator', value))
            elif field == 'date':
                terms.append(_query_term('date', value))
        # TODO: other fields as filter
        return ' '.join(terms)
