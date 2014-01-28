from __future__ import unicode_literals

import logging
import pykka
import re

from urllib import quote, unquote

from mopidy import backend

from .client import InternetArchiveClient
from .library import InternetArchiveLibraryProvider
from .playback import InternetArchivePlaybackProvider


logger = logging.getLogger(__name__)

URI_SCHEME = 'internetarchive'

URI_RE = re.compile(r"""
    (?:(?P<scheme>[^:/?#]+):)?
    (?://(?P<authority>[^/?#]*))?
    (?P<path>[^?#]*)
    (?:\?(?P<query>[^#]*))?
    (?:\#(?P<fragment>.*))?
    """, flags=(re.UNICODE | re.VERBOSE))


class InternetArchiveBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(InternetArchiveBackend, self).__init__()
        self.client = InternetArchiveClient(
            config[URI_SCHEME]['base_url'])
        self.library = InternetArchiveLibraryProvider(
            backend=self, config=config[URI_SCHEME])
        self.playback = InternetArchivePlaybackProvider(
            audio=audio, backend=self)
        self.uri_schemes = [URI_SCHEME]

    def make_track_uri(self, identifier, filename):
        uri = '%s:%s#%s' % (URI_SCHEME, quote(identifier), quote(filename))
        logger.debug('track uri [%s, %s] -> %s', identifier, filename, uri)
        return uri

    def make_album_uri(self, identifier):
        uri = '%s:%s' % (URI_SCHEME, quote(identifier))
        logger.debug('album uri [%s] -> %s', identifier, uri)
        return uri

    def make_artist_uri(self, creator):
        # FIXME: better support for artist lookup
        query = 'creator:"%s" AND mediatype:(audio OR etree)' % creator
        uri = self.make_search_uri(query)
        logger.debug('artist uri [%s] -> %s', creator, uri)
        return uri

    def make_search_uri(self, query):
        uri = '%s:?%s' % (URI_SCHEME, quote(query))
        logger.debug('search uri [%s] -> %s', query, uri)
        return uri

    def parse_uri(self, uri):
        match = URI_RE.match(uri)
        if match:
            groups = match.groupdict()
            for k in groups.keys():
                if groups[k]:
                    groups[k] = unquote(groups[k])
            return groups
        else:
            return None
