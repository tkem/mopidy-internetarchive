from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Playlist

from . import Extension

logger = logging.getLogger(__name__)


class InternetArchivePlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, config, backend):
        super(InternetArchivePlaylistsProvider, self).__init__(backend)
        self._bookmarks = []
        self._username = config[Extension.ext_name]['username']
        self._playlist = Playlist(
            uri='%s://%s/bookmarks' % (Extension.ext_name, self._username),
            name='Internet Archive Bookmarks'
        )
        self.playlists = [self._playlist]

    def create(self, name):
        pass  # TODO

    def delete(self, uri):
        pass  # TODO

    def lookup(self, uri):
        for playlist in self.playlists:
            if playlist.uri == uri:
                return playlist
        return None

    def refresh(self):
        try:
            bookmarks = self.backend.client.bookmarks(self._username)
            logger.info('Loaded %d Internet Archive bookmarks', len(bookmarks))
            if bookmarks == self._bookmarks:
                return  # unchanged
            # FIXME: this can probably be removed when playlists return refs...
            tracks = self._tracks(bookmarks)
            logger.info('Loaded %d Internet Archive tracks', len(tracks))
            self.playlists = [self._playlist.copy(tracks=tracks)]
            backend.BackendListener.send('playlists_loaded')
            self._bookmarks = bookmarks
        except Exception as e:
            logger.error('Error loading Internet Archive bookmarks: %s', e)

    def save(self, playlist):
        pass  # TODO

    def _tracks(self, bookmarks):
        tracks = []
        for doc in bookmarks:
            tracks.extend(self.backend.library._lookup(doc['identifier']))
        return tracks
