from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from . import Extension
from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider
from .bookmarks import InternetArchiveBookmarksActor
from .playlists import InternetArchivePlaylistsProvider

logger = logging.getLogger(__name__)


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = [Extension.ext_name]

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()

        ext_config = config[Extension.ext_name]
        base_url = ext_config['base_url']
        username = ext_config['username']
        timeout = ext_config['timeout']

        self.client = InternetArchiveClient(base_url, timeout)
        self.library = InternetArchiveLibraryProvider(config, self)
        self.playback = InternetArchivePlaybackProvider(audio, self)

        if username:
            self.bookmarks = InternetArchiveBookmarksActor.start(
                username, backend=self
            ).proxy()
            self.playlists = InternetArchivePlaylistsProvider(self)
        else:
            self.bookmarks = None
            self.playlists = None

    def on_start(self):
        if self.bookmarks:
            self.bookmarks.refresh()

    def on_stop(self):
        if self.bookmarks:
            self.bookmarks.stop()
