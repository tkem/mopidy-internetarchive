from __future__ import unicode_literals

import logging
import re

from collections import defaultdict

from mopidy import backend
from mopidy.models import SearchResult, Track, Album, Artist, Ref

from .translators import creator_to_artists, parse_length, parse_date


logger = logging.getLogger(__name__)

SEARCH_FIELDS = ['identifier', 'title', 'creator', 'date', 'publicdate']


class InternetArchiveLibraryProvider(backend.LibraryProvider):

    root_directory = Ref(
        uri='internetarchive:/browser',
        name='Internet Archive',
        type=Ref.DIRECTORY)


    def __init__(self, backend, config):
        super(InternetArchiveLibraryProvider, self).__init__(backend)
        self.config = config
        self.formats = [fmt.lower() for fmt in config['formats']]


    def browse(self, path):
        raise Exception('browse:' + path)
        return [self.root_directory]


    def lookup(self, uri):
        client = self.backend.client
        try:
            u = self.backend.parse_uri(uri)
            if u['query']:
                result = client.search(
                    u['query'],
                    fields=['identifier'],
                    rows=self.config['search_limit'])
                items = [client.metadata(doc['identifier']) for doc in result]
            elif u['path']:
                items = [client.metadata(u['path'])]
            else:
                logger.error('invalid uri "%s"', uri)
                return []
            tracks = []
            for item in items:
                tracks += self._item_to_tracks(item, u['fragment'])
            return tracks

        except Exception as error:
            logger.error('Failed to lookup %s: %s', uri, error)
            return []

    def search(self, query=None, uris=None):
        if not query:
            return
        result = self.backend.client.search(
            self._query_to_string(query),
            fields=SEARCH_FIELDS,
            rows=self.config['search_limit'])
        albums = [self._metadata_to_album(doc) for doc in result.docs]
        return SearchResult(
            uri=self.backend.make_search_uri(result.query),
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
        terms.append('collection:(' + ' OR '.join(self.config['collections']) + ')')
        terms.append('mediatype:(' + ' OR '.join(self.config['mediatypes']) + ')')
        terms.append('format:(' + ' OR '.join(self.config['formats']) + ')')
        return ' '.join(terms)

    def _query_value_to_string(self, value):
        if hasattr(value, '__iter__'):
            return '(' + ' OR '.join(value) + ')'
        else:
            return value

    def _metadata_to_album(self, meta):
        return Album(
            uri=self.backend.make_album_uri(meta['identifier']),
            name=meta.get('title', meta['identifier']),
            artists=creator_to_artists(meta.get('creator')),
            date=parse_date(meta.get('date', meta.get('publicdate')))
        )

    def _item_to_tracks(self, item, filename=None):
        if not item:
            logger.error('null item')
            return []

        ident = item['metadata']['identifier']
        album = self._metadata_to_album(item['metadata'])
        byname = {f['name']: f for f in item['files']}

        if filename:
            files = [f for f in item['files'] if f['name'] == filename]
        else:
            files = self._filter_formats(item['files'])

        tracks = []
        for f in files:
            if 'original' in f and f['original'] in byname:
                orig = byname[f['original']]
                for k in orig:
                    if not k in f or f[k] in ('', 'tmp'):
                        f[k] = orig[k]
                #f = dict(byname[f['original']].items() + f.items())
            kwargs = {
                'uri': self.backend.make_track_uri(ident, f['name']),
                'name': f.get('title', f['name']),
                'artists': album.artists,
                'album': album,
                'date': album.date,
                'last_modified': int(f['mtime'])
            }
            if 'creator' in f:
                kwargs['artists'] = creator_to_artists(f['creator'])
            if 'track' in f:
                kwargs['track_no'] = int(f['track'])
            if 'date' in f:
                kwargs['date'] = parse_date(f['date'])
            if 'length' in f:
                kwargs['length'] = parse_length(f['length'])
            if 'bitrate' in f:
                kwargs['bitrate'] = int(float(f['bitrate']))
            tracks.append(Track(**kwargs))
        return sorted(tracks, key=lambda t: t.track_no or t.name)

    def _filter_formats(self, files):
        byformat = defaultdict(list)
        for f in files:
            byformat[f['format'].lower()].append(f)
        for fmt in self.formats:
            if fmt in byformat:
                return byformat[fmt]
            for k in byformat.keys():
                if k.endswith(fmt):
                    return byformat[k]
        # TODO: random/default format?
        return []
