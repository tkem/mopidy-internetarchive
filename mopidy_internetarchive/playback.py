from __future__ import unicode_literals

from mopidy import backend

import uritools


class InternetArchivePlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        # archive.org identifiers and filenames are URI-safe
        _, _, identifier, _, filename = uritools.urisplit(uri)
        return self.backend.client.geturl(identifier, filename)
