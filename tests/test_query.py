from __future__ import unicode_literals

import unittest

from mopidy.models import Artist, Album, Track, Ref
from mopidy_internetarchive.query import Query


def anycase(*strings):
    return [s.upper() for s in strings] + [s.lower() for s in strings]


class QueryTest(unittest.TestCase):

    def assertQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=False)
        self.assertTrue(query.match(model))

    def assertNotQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=False)
        self.assertFalse(query.match(model))

    def assertExactQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=True)
        self.assertTrue(query.match(model))

    def assertNotExactQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=True)
        self.assertFalse(query.match(model))

    def test_create_query(self):
        for exact in (True, False):
            q1 = Query(dict(any='foo'), exact)
            self.assertEqual(len(q1), 1)
            self.assertItemsEqual(q1, ['any'])
            self.assertEqual(len(q1['any']), 1)
            self.assertEqual(q1['any'][0], 'foo')
            self.assertNotEqual(q1['any'][0], 'bar')

            q2 = Query(dict(any=['foo', 'bar'], artist='x'), exact)
            self.assertEqual(len(q2), 2)
            self.assertItemsEqual(q2, ['any', 'artist'])
            self.assertEqual(len(q2['any']), 2)
            self.assertEqual(len(q2['artist']), 1)
            self.assertEqual(q2['any'][0], 'foo')
            self.assertEqual(q2['any'][1], 'bar')
            self.assertEqual(q2['artist'][0], 'x')

        q1 = Query(dict(any='foo'), False)
        q2 = Query(dict(any='foo'), True)
        # so we can distinguish them in logs, etc.
        self.assertNotEqual(repr(q1['any'][0]), repr(q2['any'][0]))

    def test_query_errors(self):
        for exact in (True, False):
            with self.assertRaises(LookupError):
                Query(None, exact)
            with self.assertRaises(LookupError):
                Query({}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': None}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': ''}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': []}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': ['']}, exact)
            with self.assertRaises(LookupError):
                Query({'any': None}, exact)
            with self.assertRaises(LookupError):
                Query({'any': ''}, exact)
            with self.assertRaises(LookupError):
                Query({'any': []}, exact)
            with self.assertRaises(LookupError):
                Query({'any': ['']}, exact)
            with self.assertRaises(LookupError):
                Query({'foo': 'bar'}, exact)
            with self.assertRaises(TypeError):
                q = Query(dict(any='foo'), exact)
                q.match(Ref(name='foo'))

    def test_match_artist(self):
        artist = Artist(name='foo')

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(artist, any=name)
            self.assertQueryMatches(artist, artist=name)

        self.assertExactQueryMatches(artist, any='foo')
        self.assertExactQueryMatches(artist, artist='foo')

        self.assertNotQueryMatches(artist, any='none')
        self.assertNotQueryMatches(artist, artist='none')

        self.assertNotExactQueryMatches(artist, any='none')
        self.assertNotExactQueryMatches(artist, artist='none')

    def test_match_album(self):
        artist = Artist(name='foo')
        album = Album(name='bar', artists=[artist])

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(album, any=name)
            self.assertQueryMatches(album, artist=name)
            self.assertQueryMatches(album, albumartist=name)
        for name in anycase('b', 'a', 'ba', 'ar', 'bar'):
            self.assertQueryMatches(album, any=name)
            self.assertQueryMatches(album, album=name)

        self.assertExactQueryMatches(album, any='foo')
        self.assertExactQueryMatches(album, artist='foo')
        self.assertExactQueryMatches(album, albumartist='foo')
        self.assertExactQueryMatches(album, any='bar')
        self.assertExactQueryMatches(album, album='bar')

        self.assertNotQueryMatches(album, any='none')
        self.assertNotQueryMatches(album, artist='bar')
        self.assertNotQueryMatches(album, album='foo')

        self.assertNotExactQueryMatches(album, any='none')
        self.assertNotExactQueryMatches(album, artist='bar')
        self.assertNotExactQueryMatches(album, album='foo')

    def test_match_track(self):
        artist = Artist(name='foo')
        album = Album(name='bar', artists=[Artist(name='v/a')])
        track = Track(name='zyx', album=album, artists=[artist])

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, artist=name)
        for name in anycase('b', 'a', 'ba', 'ar', 'bar'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, album=name)
        for name in anycase('v', '/', 'v/', '/a', 'v/a'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, albumartist=name)
        for name in anycase('z', 'y', 'zy', 'yx', 'zyx'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, track_name=name)

        self.assertExactQueryMatches(track, any='foo')
        self.assertExactQueryMatches(track, artist='foo')
        self.assertExactQueryMatches(track, any='bar')
        self.assertExactQueryMatches(track, album='bar')
        self.assertExactQueryMatches(track, any='v/a')
        self.assertExactQueryMatches(track, albumartist='v/a')
        self.assertExactQueryMatches(track, any='zyx')
        self.assertExactQueryMatches(track, track_name='zyx')

        self.assertNotQueryMatches(track, any='none')
        self.assertNotQueryMatches(track, artist='bar')
        self.assertNotQueryMatches(track, album='foo')
        self.assertNotQueryMatches(track, albumartist='zyx')
        self.assertNotQueryMatches(track, track_name='v/a')

        self.assertNotExactQueryMatches(track, any='none')
        self.assertNotExactQueryMatches(track, artist='bar')
        self.assertNotExactQueryMatches(track, album='foo')
        self.assertNotExactQueryMatches(track, albumartist='zyx')
        self.assertNotExactQueryMatches(track, track_name='v/a')
