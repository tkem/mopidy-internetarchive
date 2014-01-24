from __future__ import unicode_literals

from mopidy import backend


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def play(self, track):
        u = self.backend.parse_uri(track.uri)
        uri = self.backend.client.get_download_url(u['path'], u['fragment'])
        track = track.copy(uri=uri)
        return super(InternetArchivePlaybackProvider, self).play(track)
