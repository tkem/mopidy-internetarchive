from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .iaclient import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider
from .lrucache import LRUCache

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    SCHEME = 'internetarchive'

    uri_schemes = [SCHEME]

    _cache = None

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.config = config

        base_url = config[self.SCHEME]['base_url']
        timeout = config[self.SCHEME]['timeout']
        cache_size = config[self.SCHEME]['cache_size']
        cache_ttl = config[self.SCHEME]['cache_ttl']

        logger.debug("Internet Archive URL=%s, timeout=%r, cache=%r",
                     base_url, timeout, (cache_size, cache_ttl))
        if cache_size and cache_ttl:
            cache = LRUCache(maxsize=cache_size, ttl=cache_ttl)
        else:
            cache = None
        self.client = InternetArchiveClient(base_url, timeout, cache=cache)
        self.library = InternetArchiveLibraryProvider(self)
        self.playback = InternetArchivePlaybackProvider(audio, self)
