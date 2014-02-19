from __future__ import unicode_literals

from mopidy import backend


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=self.backend.library.get_stream_url(track.uri))
        return super(InternetArchivePlaybackProvider, self).change_track(track)
