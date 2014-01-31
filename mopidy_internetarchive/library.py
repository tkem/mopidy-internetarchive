from __future__ import unicode_literals

import logging
import re

from collections import defaultdict

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .translators import item_to_tracks, file_to_ref, doc_to_ref, doc_to_album
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)

SPECIAL_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')


def _build_query(*terms):
    return ' AND '.join(terms)


def _quote_term(term):
    term = SPECIAL_CHAR_RE.sub(r'\\\1', term)
    # only quote if term contains whitespace, since something like
    # date:"2014-01-01" will give an error
    if any(c.isspace() for c in term):
        term = '"' + term + '"'
    return term


def _build_term(field, values):
    if not hasattr(values, '__iter__'):
        values = [values]
    values = [_quote_term(value) for value in values]
    if len(values) > 1:
        term = '(%s)' % ' OR '.join(values)
    else:
        term = values[0]
    return '%s:%s' % (field, term) if field else term


def _byname(files, name):
    for f in files:
        if f['name'] == name:
            return [f]
    return []


def _byformat(files, formats):
    formats = [fmt.lower() for fmt in formats]
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
        self.root_directory = doc_to_ref({
            'identifier': '',
            'title': self.getconfig('browse_label')
        }, Ref.DIRECTORY)

    def browse(self, uri):
        logger.debug("internetarchive browse: %s", uri)

        if not uri:
            return [self.root_directory]
        if uri == self.root_directory.uri:
            return self._browse_root()

        item = self.backend.client.getitem(urisplit(uri).path)

        if item['metadata']['mediatype'] == 'collection':
            return self._browse_collection(item['metadata']['identifier'])
        elif item['metadata']['mediatype'] in self.getconfig('mediatypes'):
            return self._browse_audio(item)
        else:
            return []

    def lookup(self, uri):
        logger.debug("internetarchive lookup: %s", uri)

        try:
            uriparts = urisplit(uri)
            item = self.backend.client.getitem(uriparts.path)
            if uriparts.fragment:
                files = _byname(item['files'], uriparts.fragment)
            else:
                files = _byformat(item['files'], self.getconfig('formats'))
            logger.debug("internetarchive files: %r", files)
            return item_to_tracks(item, files)
        except Exception as error:
            logger.error('internetarchive lookup %s: %s', uri, error)
            return []

    def search(self, query=None, uris=None):
        logger.debug("internetarchive search: %r", query)

        if not query:
            return
        terms = [
            _build_term('collection', self.getconfig('collections')),
            _build_term('mediatype', self.getconfig('mediatypes')),
            _build_term('format', self.getconfig('formats'))
        ]
        for (field, value) in query.iteritems():
            if field == "any":
                terms.append(_build_term(None, value))
            elif field == "album":
                terms.append(_build_term('title', value))
            elif field == "artist":
                terms.append(_build_term('creator', value))
            elif field == 'date':
                terms.append(_build_term('date', value))
            # TODO: other fields as filter
        result = self.backend.client.search(
            query=_build_query(*terms),
            fields=self.SEARCH_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('search_limit'))
        logger.debug("internetarchive search result: %r", result)
        return SearchResult(
            uri=uricompose(self.backend.URI_SCHEME, query=result.query),
            albums=[doc_to_album(doc) for doc in result.docs])

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def _browse_root(self):
        result = self.backend.client.search(
            query=_build_query(
                'mediatype:collection',
                _build_term('identifier', self.getconfig('collections'))),
            fields=self.BROWSE_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('browse_limit'))
        logger.debug("internetarchive search result: %r", result)
        return [doc_to_ref(doc, Ref.DIRECTORY) for doc in result.docs]

    def _browse_collection(self, identifier):
        result = self.backend.client.search(
            query=_build_query(
                _build_term('collection', identifier),
                _build_term('mediatype', self.getconfig('mediatypes')),
                _build_term('format', self.getconfig('formats'))),
            fields=self.BROWSE_FIELDS,
            sort=self.getconfig('sort_order'),
            rows=self.getconfig('browse_limit'))
        logger.debug("internetarchive search result: %r", result)
        return [doc_to_ref(doc, Ref.DIRECTORY) for doc in result.docs]

    def _browse_audio(self, item):
        files = _byformat(item['files'], self.getconfig('formats'))
        logger.debug("internetarchive files: %r", files)
        return [file_to_ref(item, f) for f in files]
