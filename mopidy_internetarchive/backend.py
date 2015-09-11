from __future__ import unicode_literals

import cachetools

from mopidy import backend, httpclient

import pykka

from . import Extension
from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider


def _cache(cache_size=None, cache_ttl=None, **kwargs):
    if cache_size is None:
        return None
    elif cache_ttl is None:
        return cachetools.LRUCache(cache_size)
    else:
        return cachetools.TTLCache(cache_size, cache_ttl)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = [Extension.ext_name]

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()

        self.client = client = InternetArchiveClient(
            config[Extension.ext_name]['base_url'],
            retries=config[Extension.ext_name]['retries'],
            timeout=config[Extension.ext_name]['timeout']
        )
        product = '%s/%s' % (Extension.dist_name, Extension.version)
        client.useragent = httpclient.format_user_agent(product)
        proxy = httpclient.format_proxy(config['proxy'])
        client.proxies.update({'http': proxy, 'https': proxy})
        client.cache = _cache(**config[Extension.ext_name])

        self.library = InternetArchiveLibraryProvider(config, self)
        self.playback = InternetArchivePlaybackProvider(audio, self)
