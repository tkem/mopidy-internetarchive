from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from . import Extension
from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider
from .playlists import InternetArchivePlaylistsProvider

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = [Extension.ext_name]

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.client = InternetArchiveClient(
            config[Extension.ext_name]['base_url'],
            config[Extension.ext_name]['timeout'],
        )
        self.library = InternetArchiveLibraryProvider(config, self)
        self.playback = InternetArchivePlaybackProvider(audio, self)

        if config[Extension.ext_name]['username']:
            self.playlists = InternetArchivePlaylistsProvider(config, self)

    def on_start(self):
        # give other backends a chance to load, too...
        if self.playlists:
            self.playlists.refresh()
        super(InternetArchiveBackend, self).on_start()
