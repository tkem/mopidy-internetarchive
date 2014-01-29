from __future__ import unicode_literals

import logging

from mopidy import backend
from uritools import urisplit

logger = logging.getLogger(__name__)


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def play(self, track):
        uriparts = urisplit(track.uri)
        uri = self.backend.client.geturl(uriparts.path, uriparts.fragment)
        logger.debug("internetarchive playback uri: %s", uri)
        track = track.copy(uri=uri)
        return super(InternetArchivePlaybackProvider, self).play(track)
