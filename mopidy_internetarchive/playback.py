from __future__ import unicode_literals

from mopidy import backend

import logging
import uritools

logger = logging.getLogger(__name__)


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        parts = uritools.urisplit(track.uri)
        identifier, filename = parts.getpath(), parts.getfragment()
        t = track.copy(uri=self.backend.client.geturl(identifier, filename))
        return super(InternetArchivePlaybackProvider, self).change_track(t)
