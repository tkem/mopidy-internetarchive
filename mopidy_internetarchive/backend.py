from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .iaclient import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    SCHEME = 'internetarchive'

    uri_schemes = [SCHEME]

    _cache = None

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.config = config
        self.client = InternetArchiveClient(
            config[self.SCHEME]['base_url'],
            cache=self.cache
        )
        self.library = InternetArchiveLibraryProvider(self)
        self.playback = InternetArchivePlaybackProvider(audio, self)

    @property
    def cache(self):
        from .lrucache import LRUCache
        if self._cache is None:
            config = self.config[self.SCHEME]
            self._cache = LRUCache(config['cache_size'], config['cache_ttl'])
        return self._cache
