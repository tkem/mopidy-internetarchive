from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Playlist

from . import Extension

logger = logging.getLogger(__name__)


class InternetArchiveBookmarks(pykka.ThreadingActor):

    pykka_traversable = True

    def __init__(self, username, backend):
        super(InternetArchiveBookmarks, self).__init__()
        self.username = username
        # always access backend by proxy
        self.backend = backend.actor_ref.proxy()
        # for delaying work to our future self
        self.future = self.actor_ref.proxy()

    def refresh(self):
        try:
            bookmarks = self.backend.client.bookmarks(self.username).get()
            logger.debug('Received %d Archive bookmarks', len(bookmarks))
            self.future.load(bookmarks)
        except pykka.ActorDeadError:
            self.stop()
        except Exception as e:
            logger.error('Error loading Archive bookmarks: %s', e)

    def load(self, bookmarks, playlists=[]):
        playlists = playlists[:]
        try:
            if bookmarks:
                doc = bookmarks.pop(0)
                id = doc['identifier']
                uri = '%s:%s' % (Extension.ext_name, id)
                name = doc.get('title', id)
                tracks = self.backend.library.lookup(uri).get()
                if tracks:
                    playlists += [Playlist(uri=uri, name=name, tracks=tracks)]
                else:
                    logger.warn('Skipping empty Archive bookmark %s', name)
                self.future.load(bookmarks, playlists)
            else:
                logger.info('Loaded %d Archive bookmarks', len(playlists))
                self.backend.playlists.playlists = playlists
                backend.BackendListener.send('playlists_loaded')
        except pykka.ActorDeadError:
            self.stop()
        except Exception as e:
            logger.error('Error loading Archive bookmarks: %s', e)


class InternetArchivePlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, config, backend):
        super(InternetArchivePlaylistsProvider, self).__init__(backend)
        username = config[Extension.ext_name]['username']
        if username:
            self.bookmarks = InternetArchiveBookmarks.start(username, backend)
        else:
            self.bookmarks = None
        self.timeout = config[Extension.ext_name]['timeout']

    def create(self, name):
        pass  # TODO

    def delete(self, uri):
        pass  # TODO

    def lookup(self, uri):
        for playlist in self.playlists:
            if playlist.uri == uri:
                return playlist
        return None

    def refresh(self):
        if self.bookmarks:
            # clear library cache
            self.backend.library.refresh()
            self.bookmarks.proxy().refresh()

    def save(self, playlist):
        pass  # TODO

    def start(self):
        if self.bookmarks:
            self.bookmarks.proxy().refresh()

    def stop(self):
        if self.bookmarks:
            logger.debug('Stopping %s', self.bookmarks)
            try:
                self.bookmarks.stop(timeout=1)
            except pykka.Timeout:
                # bookmarks actor may be waiting on backend
                pykka.ActorRegistry.unregister(self.bookmarks)
