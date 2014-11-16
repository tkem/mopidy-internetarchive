from __future__ import unicode_literals

from mopidy import backend


class InternetArchivePlaylistsProvider(backend.PlaylistsProvider):

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
        self.backend.bookmarks.refresh()

    def save(self, playlist):
        pass  # TODO
