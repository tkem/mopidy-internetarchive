from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    URI_SCHEME = 'internetarchive'

    uri_schemes = [URI_SCHEME]

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.config = config
        self.client = InternetArchiveClient(
            config[self.URI_SCHEME]['base_url'], cache=self.cache())
        self.library = InternetArchiveLibraryProvider(
            backend=self)
        self.playback = InternetArchivePlaybackProvider(
            audio=audio, backend=self)

    def getconfig(self, name):
        return self.config[self.URI_SCHEME][name]

    def cache(self):
        from .lrucache import LRUCache
        size = self.getconfig('cache_size')
        ttl = self.getconfig('cache_ttl')
        return LRUCache(maxsize=size, ttl=ttl)
