from __future__ import unicode_literals

import unittest
import pykka

from mopidy_internetarchive.backend import InternetArchiveBackend
from mopidy import core

TEST_ARTIST = 'Martin Luther King'
TEST_ALBUM = 'I Have a Dream'
TEST_DATE = '1963-08-28'


class LibraryTest(unittest.TestCase):
    config = {
        'internetarchive': {
            'base_url': 'http://archive.org',
            'username': None,
            'collections': ('etree', 'audio'),
            'audio_formats': ('MP3'),
            'image_formats': ('JPEG'),
            'browse_limit': None,
            'browse_order': None,
            'search_limit': None,
            'search_order': None,
            'exclude_collections': (),
            'exclude_mediatypes': (),
            'cache_size': 1,
            'cache_ttl': None,
            'retries': 0,
            'timeout': None
        }
    }

    def setUp(self):
        self.backend = InternetArchiveBackend.start(
            config=self.config, audio=None).proxy()
        self.core = core.Core(backends=[self.backend])
        self.library = self.core.library

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_search_artist(self):
        self.library.search(artist=[TEST_ARTIST])
        # TODO: write tests

    def test_search_album(self):
        self.library.search(album=[TEST_ALBUM])
        # TODO: write tests

    def test_search_date(self):
        self.library.search(date=[TEST_DATE])
        # TODO: write tests
