import logging
import re

from mopidy.backends import base
from mopidy.models import Track

logger = logging.getLogger('mopidy.backends.internetarchive')

URI_RE = re.compile('^internetarchive://([^/]+)/([^/]+)$')


class InternetArchivePlaybackProvider(base.BasePlaybackProvider):

    def play(self, track):
        if not track.uri:
            return False
        obj = self.backend.parse_uri(track.uri)
        if not obj:
            return False
        track = Track(
            uri=self.backend.client.get_download_url(obj['path'], obj['fragment'])
        )
        return super(InternetArchivePlaybackProvider, self).play(track)
