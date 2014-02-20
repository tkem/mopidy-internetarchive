from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Album, Track, SearchResult, Ref

from .parsing import *  # noqa
from .query import Query
from .uritools import urisplit, uriunsplit

logger = logging.getLogger(__name__)


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    BROWSE_FIELDS = ('identifier', 'title', 'mediatype'),

    SEARCH_FIELDS = ('identifier', 'title', 'creator', 'date', 'publicdate')

    def __init__(self, backend):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.root_directory = Ref.directory(
            uri=uriunsplit([backend.SCHEME, None, '/', None, None]),
            name=self.config['browse_label']
        )
        self.browse_query = self.backend.client.query_string({
            'mediatype': self.config['mediatypes'],
            'format': self.config['formats']
        }, group='OR')
        self.search_query = self.backend.client.query_string({
            'collection': self.config['collections'],
            'mediatype':  self.config['mediatypes'],
            'format': self.config['formats']
        }, group='OR')
        self.bookmarks = self._load_bookmarks(self.config['bookmarks'])
        self.collections = self._load_collections(self.config['collections'])

    @property
    def config(self):
        return self.backend.config[self.backend.SCHEME]

    def browse(self, uri):
        logger.debug("internetarchive browse %r", uri)

        try:
            if not uri:
                return [self.root_directory]
            elif uri == self.root_directory.uri:
                return self._browse_root()
            elif uri in self.bookmarks:
                return self._browse_bookmarks(urisplit(uri).userinfo)
            elif uri in self.collections:
                return self._browse_collection(urisplit(uri).path)
            else:
                return self._browse_item(urisplit(uri).path)
        except Exception as error:
            logger.error('Error browsing %r: %s', uri, error)
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
            return self._item_to_tracks(item, files)
        except Exception as error:
            logger.error('Lookup error for %r: %s', uri, error)
            return []

    def find_exact(self, query=None, uris=None):
        logger.debug("internetarchive find %r", query)

        if not query:
            return
        try:
            return SearchResult(albums=self._find_albums(Query(query, True)))
        except Exception as error:
            logger.error('internetarchive find %r: %s', query, error)
            return None

    def search(self, query=None, uris=None):
        logger.debug("internetarchive search %r", query)

        if not query:
            return
        try:
            return SearchResult(albums=self._find_albums(Query(query, False)))
        except Exception as error:
            logger.error('internetarchive search %r: %s', query, error)
            return None

    def get_stream_url(self, uri):
        _, _, identifier, _, filename = urisplit(uri)
        return self.backend.client.geturl(identifier.lstrip('/'), filename)

    def _load_bookmarks(self, usernames):
        refs = {}
        for username in usernames:
            try:
                # raise error if username does not exit, cache for browsing
                self.backend.client.bookmarks(username)
            except Exception as e:
                logger.error('Error loading bookmarks for %r: %s', username, e)
                continue
            uri = self._bookmarks_uri(username)
            name = self.config['bookmarks_label'].format(username)
            refs[uri] = Ref.directory(uri=uri, name=name)
        if refs:
            logger.info("Loaded %d Internet Archive bookmarks", len(refs))
        return refs

    def _load_collections(self, identifiers):
        refs = {}
        for identifier in identifiers:
            try:
                item = self.backend.client.metadata(identifier + '/metadata')
            except Exception as e:
                logger.error('Error loading collection %r: %s', identifier, e)
                continue
            if item['mediatype'] != 'collection':
                logger.error('Item %r is not a collection', identifier)
                continue
            uri = self._item_uri(identifier)
            name = parse_title(item.get('title'), identifier)
            refs[uri] = Ref.directory(uri=uri, name=name)
        if refs:
            logger.info("Loaded %d Internet Archive collections", len(refs))
        return refs

    def _browse_root(self):
        # fix temporary (e.g. network) errors at startup
        if len(self.bookmarks) != len(self.config['bookmarks']):
            missing = filter(
                lambda v: self._bookmarks_uri(v) not in self.bookmarks,
                self.config['bookmarks']
            )
            self.bookmarks.update(self._load_bookmarks(missing))
        if len(self.collections) != len(self.config['collections']):
            missing = filter(
                lambda v: self._item_uri(v) not in self.collections,
                self.config['collections']
            )
            self.collections.update(self._load_collections(missing))
        return self.bookmarks.values() + self.collections.values()

    def _browse_bookmarks(self, username):
        result = self.backend.client.bookmarks(username)
        return [self._doc_to_ref(doc) for doc in result]

    def _browse_collection(self, identifier):
        qs = self.backend.client.query_string(dict(collection=identifier))
        result = self.backend.client.search(
            self.browse_query + ' AND ' + qs,
            fields=self.BROWSE_FIELDS,
            sort=self.config['sort_order'],
            rows=self.config['browse_limit']
        )
        return [self._doc_to_ref(doc) for doc in result]

    def _browse_item(self, identifier):
        item = self.backend.client.metadata(identifier)
        if item['metadata']['mediatype'] not in self.config['mediatypes']:
            return []
        refs = []
        for f in self._files_by_format(item['files']):
            uri = self._file_uri(identifier, f['name'])
            name = parse_title(f.get('title'), f['name'])
            refs.append(Ref.track(uri=uri, name=name))
        return refs

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
        qs = self.backend.client.query_string(terms, group='AND')
        logger.debug('internetarchive query string: %r', qs)
        result = self.backend.client.search(
            self.search_query + ' AND ' + qs,
            fields=self.SEARCH_FIELDS,
            sort=self.config['sort_order'],
            rows=self.config['search_limit']
        )
        albums = [self._doc_to_album(doc) for doc in result]
        logger.debug("internetarchive found albums: %r", albums)
        return query.filter_albums(albums)

    def _bookmarks_uri(self, username):
        authority = '%s@archive.org' % username
        return uriunsplit([self.backend.SCHEME, authority, '/', None, None])

    def _item_uri(self, identifier):
        return uriunsplit([self.backend.SCHEME, None, identifier, None, None])

    def _file_uri(self, itemid, filename):
        return uriunsplit([self.backend.SCHEME, None, itemid, None, filename])

    def _doc_to_album(self, doc):
        return Album(
            uri=self._item_uri(doc['identifier']),
            name=parse_title(doc.get('title'), doc['identifier']),
            artists=parse_creator(doc.get('creator')),
            date=parse_date(doc.get('date'))
        )

    def _doc_to_ref(self, doc):
        return Ref.directory(
            uri=self._item_uri(doc['identifier']),
            name=parse_title(doc.get('title'), doc['identifier'])
        )

    def _item_to_tracks(self, item, files):
        metadata = item['metadata']
        identifier = metadata['identifier']
        album = self._doc_to_album(metadata)
        byname = {f['name']: f for f in item['files']}

        tracks = []
        for f in files:
            if 'original' in f and f['original'] in byname:
                orig = byname[f['original']]
                for key in orig:
                    if not key in f or f[key] in ('', 'tmp'):
                        f[key] = orig[key]

            tracks.append(Track(
                uri=self._file_uri(identifier, f['name']),
                name=parse_title(f.get('title'), f['name']),
                artists=parse_creator(f.get('creator'), album.artists),
                album=album,
                track_no=parse_track(f.get('track')),
                date=parse_date(f.get('date'), album.date),
                length=parse_length(f.get('length')),
                bitrate=parse_bitrate(f.get('bitrate')),
                last_modified=parse_mtime(f.get('mtime'))
            ))
        return tracks

    def _files_by_format(self, files):
        from collections import defaultdict
        byformat = defaultdict(list)
        for f in files:
            byformat[f['format'].lower()].append(f)
        for fmt in [fmt.lower() for fmt in self.config['formats']]:
            if fmt in byformat:
                return byformat[fmt]
            for key in byformat.keys():
                if fmt in key:
                    return byformat[key]
        return []
