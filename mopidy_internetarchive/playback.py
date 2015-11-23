from __future__ import unicode_literals

from mopidy import backend

from . import translator


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        identifier, filename, _ = translator.parse_uri(uri)
        return self.backend.client.geturl(identifier, filename)
