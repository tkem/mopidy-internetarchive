from __future__ import unicode_literals

import logging

from mopidy import backend, httpclient

import pykka

from . import Extension
from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = [Extension.ext_name]

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.client = InternetArchiveClient(
            config[Extension.ext_name]['base_url'],
            retries=config[Extension.ext_name]['retries'],
            timeout=config[Extension.ext_name]['timeout']
        )
        proxy = httpclient.format_proxy(config['proxy'])
        self.client.proxies.update({'http': proxy, 'https': proxy})
        agent = '%s/%s' % (Extension.dist_name, Extension.version)
        self.client.useragent = httpclient.format_user_agent(agent)
        self.library = InternetArchiveLibraryProvider(config, self)
        self.playback = InternetArchivePlaybackProvider(audio, self)
