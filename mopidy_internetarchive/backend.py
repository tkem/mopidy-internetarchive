from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider
from .lrucache import LRUCache

logger = logging.getLogger(__name__)

URI_SCHEME = 'internetarchive'


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        config = self.config = config[URI_SCHEME]
        cache = LRUCache(self.config['cache_size'], self.config['cache_ttl'])
        self.client = InternetArchiveClient(config['base_url'], cache=cache)
        self.library = InternetArchiveLibraryProvider(backend=self)
        self.playback = InternetArchivePlaybackProvider(
            audio=audio, backend=self)
        self.uri_schemes = [URI_SCHEME]
