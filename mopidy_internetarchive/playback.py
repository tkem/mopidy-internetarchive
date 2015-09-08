from __future__ import unicode_literals

import logging

from mopidy import backend

import uritools

logger = logging.getLogger(__name__)


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        parts = uritools.urisplit(uri)
        identifier, filename = parts.getpath(), parts.getfragment()
        return self.backend.client.geturl(identifier, filename)
