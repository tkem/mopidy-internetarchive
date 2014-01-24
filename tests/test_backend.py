from __future__ import unicode_literals
import unittest

from mopidy_internetarchive.backend import InternetArchiveBackend


class BackendTest(unittest.TestCase):
    config = {
        'internetarchive': {
            # FIXME: file url for tests
            'base_url': 'http://archive.org',
            'format': ['MP3']
        }
    }

    def setUp(self):
        self.backend = InternetArchiveBackend(config=self.config, audio=None)

    def test_make_track_uri(self):
        self.assertEqual(
            self.backend.make_track_uri('item1', 'file1'),
            'internetarchive:item1#file1'
        )

    def test_make_album_uri(self):
        self.assertEqual(
            self.backend.make_album_uri('item1'),
            'internetarchive:item1'
        )

    def test_make_artist_uri(self):
        pass  # TODO: write tests

    def test_make_search_uri(self):
        self.assertEqual(
            self.backend.make_search_uri('foo bar'),
            'internetarchive:?foo%20bar'
        )

    def test_parse_uri(self):
        empty = self.backend.parse_uri('internetarchive:')

        self.assertEqual(
            self.backend.parse_uri('internetarchive:item1'),
            dict(empty, path='item1')
        )
        self.assertEqual(
            self.backend.parse_uri('internetarchive:item1#file1'),
            dict(empty, path='item1', fragment='file1')
        )
        self.assertEqual(
            self.backend.parse_uri('internetarchive:?foo'),
            dict(empty, query='foo')
        )
        self.assertEqual(
            self.backend.parse_uri('internetarchive:?foo%20bar'),
            dict(empty, query='foo bar')
        )
