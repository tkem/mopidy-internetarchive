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
            # FIXME: file url for tests
            'base_url': 'http://archive.org',
            'collection': None,
            'mediatype': ['etree', 'audio'],
            'format': 'MP3',
            'limit': None
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

    def test_search_album(self):
        self.library.search(album=[TEST_ALBUM])

    def test_search_date(self):
        self.library.search(date=[TEST_DATE])


#
#    def test_search_track_name(self):
#        result = self.library.search(track_name=['Rack1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(track_name=['Rack2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#    def test_search_artist(self):
#        result = self.library.search(artist=['Tist1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(artist=['Tist2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#    def test_search_albumartist(self):
#        # Artist is both track artist and album artist
#        result = self.library.search(albumartist=['Tist1'])
#        self.assertEqual(list(result[0].tracks), [self.tracks[0]])
#
#        # Artist is both track artist and album artist
#        result = self.library.search(albumartist=['Tist2'])
#        self.assertEqual(list(result[0].tracks), [self.tracks[1]])
#
#        # Artist is just album artist
#        result = self.library.search(albumartist=['Tist3'])
#        self.assertEqual(list(result[0].tracks), [self.tracks[2]])
#
#    def test_search_composer(self):
#        result = self.library.search(composer=['Tist5'])
#        self.assertEqual(list(result[0].tracks), self.tracks[4:5])
#
#    def test_search_performer(self):
#        result = self.library.search(performer=['Tist6'])
#        self.assertEqual(list(result[0].tracks), self.tracks[5:6])
#
#    def test_search_album(self):
#        result = self.library.search(album=['Bum1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(album=['Bum2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#    def test_search_genre(self):
#        result = self.library.search(genre=['Enre1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[4:5])
#
#        result = self.library.search(genre=['Enre2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[5:6])
#
#    def test_search_date(self):
#        result = self.library.search(date=['2001'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(date=['2001-02-03'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(date=['2001-02-04'])
#        self.assertEqual(list(result[0].tracks), [])
#
#        result = self.library.search(date=['2002'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#    def test_search_track_no(self):
#        result = self.library.search(track_no=['1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(track_no=['2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#    def test_search_comment(self):
#        result = self.library.search(comment=['fantastic'])
#        self.assertEqual(list(result[0].tracks), self.tracks[3:4])
#
#        result = self.library.search(comment=['antasti'])
#        self.assertEqual(list(result[0].tracks), self.tracks[3:4])
#
#    def test_search_any(self):
#        # Matches on track artist
#        result = self.library.search(any=['Tist1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        # Matches on track composer
#        result = self.library.search(any=['Tist5'])
#        self.assertEqual(list(result[0].tracks), self.tracks[4:5])
#
#        # Matches on track performer
#        result = self.library.search(any=['Tist6'])
#        self.assertEqual(list(result[0].tracks), self.tracks[5:6])
#
#        # Matches on track
#        result = self.library.search(any=['Rack1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        result = self.library.search(any=['Rack2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[1:2])
#
#        # Matches on track album
#        result = self.library.search(any=['Bum1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#        # Matches on track album artists
#        result = self.library.search(any=['Tist3'])
#        self.assertEqual(
#            list(result[0].tracks), [self.tracks[3], self.tracks[2]])
#
#        # Matches on track genre
#        result = self.library.search(any=['Enre1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[4:5])
#
#        result = self.library.search(any=['Enre2'])
#        self.assertEqual(list(result[0].tracks), self.tracks[5:6])
#
#        # Matches on track comment
#        result = self.library.search(any=['fanta'])
#        self.assertEqual(list(result[0].tracks), self.tracks[3:4])
#
#        result = self.library.search(any=['is a fan'])
#        self.assertEqual(list(result[0].tracks), self.tracks[3:4])
#
#        # Matches on URI
#        result = self.library.search(any=['TH1'])
#        self.assertEqual(list(result[0].tracks), self.tracks[:1])
#
#    def test_search_wrong_type(self):
#        test = lambda: self.library.search(wrong=['test'])
#        self.assertRaises(LookupError, test)
#
#    def test_search_with_empty_query(self):
#        test = lambda: self.library.search(artist=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(albumartist=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(composer=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(performer=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(track_name=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(album=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(genre=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(date=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(comment=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(uri=[''])
#        self.assertRaises(LookupError, test)
#
#        test = lambda: self.library.search(any=[''])
#        self.assertRaises(LookupError, test)
