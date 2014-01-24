from __future__ import unicode_literals

import logging
import pykka
import re

from mopidy.backends import base

from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider


logger = logging.getLogger('mopidy.backends.internetarchive')

URI_SCHEME = 'internetarchive'

URI_RE = re.compile(r"""
    (?:(?P<scheme>[^:/?#]+):)?
    (?://(?P<authority>[^/?#]*))?
    (?P<path>[^?#]*)
    (?:\?(?P<query>[^#]*))?
    (?:\#(?P<fragment>.*))?
    """, flags=(re.UNICODE | re.VERBOSE))


class InternetArchiveBackend(pykka.ThreadingActor, base.Backend):

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.client = InternetArchiveClient(
            config[URI_SCHEME]['base_url'])
        self.library = InternetArchiveLibraryProvider(
            backend=self, config=config[URI_SCHEME])
        self.playback = InternetArchivePlaybackProvider(
            audio=audio, backend=self)
        self.uri_schemes = [URI_SCHEME]

    def make_track_uri(self, identifier, filename):
        return URI_SCHEME + ':' + identifier + '#' + filename

    def make_album_uri(self, identifier):
        return URI_SCHEME + ':' + identifier

    def make_artist_uri(self, creator):
        return self.make_search_uri('creator:"%s"' % creator)

    def make_search_uri(self, query):
        return URI_SCHEME + ':?' + query

    def parse_uri(self, uri):
        match = URI_RE.match(uri)
        if match:
            return match.groupdict()
        else:
            return None
