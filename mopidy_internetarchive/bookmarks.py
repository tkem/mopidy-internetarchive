from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Playlist

from . import Extension

logger = logging.getLogger(__name__)


class InternetArchiveBookmarksActor(pykka.ThreadingActor):

    pykka_traversable = True

    def __init__(self, username, backend):
        super(InternetArchiveBookmarksActor, self).__init__()
        self.username = username
        self.backend = backend

    def refresh(self):
        # access backend properties by proxy
        proxy = self.backend.actor_ref.proxy()
        try:
            docs = proxy.client.bookmarks(self.username).get()
            logger.debug('Loaded %d Internet Archive bookmarks', len(docs))
            playlists = []
            for doc in docs:
                uri = '%s:%s' % (Extension.ext_name, doc['identifier'])
                name = doc.get('title', uri)
                tracks = proxy.library.lookup(uri).get()
                playlists.append(Playlist(uri=uri, name=name, tracks=tracks))
            logger.info('Loaded %d Internet Archive playlists', len(playlists))
            proxy.playlists.playlists = playlists
            backend.BackendListener.send('playlists_loaded')
        except Exception as e:
            logger.error('Error loading Internet Archive bookmarks: %s', e)
