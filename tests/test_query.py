from __future__ import unicode_literals

import unittest

from mopidy.models import Artist, Album, Track
from mopidy_internetarchive.query import Query


def normcase(*strings):
    return [s.upper() for s in strings] + [s.lower() for s in strings]


class ParsingTest(unittest.TestCase):

    artists = {name: Artist(name=name) for name in [
        'foo', 'FOO', 'bar', 'BAR'
    ]}

    albums = {kwargs['name']: Album(**kwargs) for kwargs in [
        dict(name='foo', artists=[artists['foo']]),
        dict(name='FOO', artists=[artists['FOO']]),
        dict(name='bar', artists=[artists['bar']]),
        dict(name='BAR', artists=[artists['bar']]),
    ]}

    tracks = {kwargs['name']: Track(**kwargs) for kwargs in [
        dict(name='foo', artists=[artists['foo']], album=albums['foo']),
        dict(name='FOO', artists=[artists['FOO']], album=albums['FOO']),
        dict(name='bar', artists=[artists['bar']], album=albums['bar']),
        dict(name='BAR', artists=[artists['BAR']], album=albums['bar']),
    ]}

    def test_create_query(self):
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

    def test_filter_artists(self):
        def q(**kwargs):
            query = Query(kwargs, exact=False)
            return query.filter_artists(self.artists.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])

        for artist in normcase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertItemsEqual(
                q(any=artist),
                [self.artists['foo'], self.artists['FOO']]
            )
            self.assertItemsEqual(
                q(artist=artist),
                [self.artists['foo'], self.artists['FOO']]
            )

    def test_filter_artists_exact(self):
        def q(**kwargs):
            query = Query(kwargs, exact=True)
            return query.filter_artists(self.artists.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])

        self.assertEqual(q(any='foo'), [self.artists['foo']])
        self.assertEqual(q(artist='foo'), [self.artists['foo']])
        self.assertEqual(q(any='FOO'), [self.artists['FOO']])
        self.assertEqual(q(artist='FOO'), [self.artists['FOO']])

    def test_filter_albums(self):
        def q(**kwargs):
            query = Query(kwargs, exact=False)
            return query.filter_albums(self.albums.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])
        self.assertEqual(q(album='x'), [])
        self.assertEqual(q(albumartist='x'), [])

        for name in normcase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertItemsEqual(
                q(any=name),
                [self.albums['foo'], self.albums['FOO']]
            )
            self.assertItemsEqual(
                q(artist=name),
                [self.albums['foo'], self.albums['FOO']]
            )
            self.assertItemsEqual(
                q(album=name),
                [self.albums['foo'], self.albums['FOO']]
            )
            self.assertItemsEqual(
                q(albumartist=name),
                [self.albums['foo'], self.albums['FOO']]
            )

        self.assertItemsEqual(
            q(album='foo', albumartist='foo'),
            [self.albums['foo'], self.albums['FOO']]
        )
        self.assertItemsEqual(
            q(album='foo', albumartist='bar'),
            []
        )
        self.assertItemsEqual(
            q(albumartist='bar'),
            [self.albums['bar'], self.albums['BAR']]
        )
        self.assertItemsEqual(
            q(album='bar', albumartist='bar'),
            [self.albums['bar'], self.albums['BAR']]
        )

    def test_filter_albums_exact(self):
        def q(**kwargs):
            query = Query(kwargs, exact=True)
            return query.filter_albums(self.albums.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])
        self.assertEqual(q(album='x'), [])
        self.assertEqual(q(albumartist='x'), [])

        self.assertEqual(q(any='foo'), [self.albums['foo']])
        self.assertEqual(q(artist='foo'), [self.albums['foo']])
        self.assertEqual(q(album='foo'), [self.albums['foo']])
        self.assertEqual(q(albumartist='foo'), [self.albums['foo']])

        self.assertItemsEqual(
            q(album='foo', albumartist='foo'),
            [self.albums['foo']]
        )
        self.assertItemsEqual(
            q(album='foo', albumartist='bar'),
            []
        )
        self.assertItemsEqual(
            q(albumartist='bar'),
            [self.albums['bar'], self.albums['BAR']]
        )
        self.assertItemsEqual(
            q(album='bar', albumartist='bar'),
            [self.albums['bar']]
        )

    def test_filter_tracks(self):
        def q(**kwargs):
            query = Query(kwargs, exact=False)
            return query.filter_tracks(self.tracks.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])
        self.assertEqual(q(album='x'), [])
        self.assertEqual(q(albumartist='x'), [])
        self.assertEqual(q(track_name='x'), [])

        for name in normcase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertItemsEqual(
                q(any=name),
                [self.tracks['foo'], self.tracks['FOO']]
            )
            self.assertItemsEqual(
                q(artist=name),
                [self.tracks['foo'], self.tracks['FOO']]
            )
            self.assertItemsEqual(
                q(album=name),
                [self.tracks['foo'], self.tracks['FOO']]
            )
            self.assertItemsEqual(
                q(albumartist=name),
                [self.tracks['foo'], self.tracks['FOO']]
            )
            self.assertItemsEqual(
                q(track_name=name),
                [self.tracks['foo'], self.tracks['FOO']]
            )

        self.assertItemsEqual(
            q(track_name='foo', artist='foo'),
            [self.tracks['foo'], self.tracks['FOO']]
        )
        self.assertItemsEqual(
            q(track_name='foo', artist='bar'),
            []
        )
        self.assertItemsEqual(
            q(album='bar'),
            [self.tracks['bar'], self.tracks['BAR']]
        )
        self.assertItemsEqual(
            q(artist='bar'),
            [self.tracks['bar'], self.tracks['BAR']]
        )

    def test_filter_tracks_exact(self):
        def q(**kwargs):
            query = Query(kwargs, exact=True)
            return query.filter_tracks(self.tracks.values())

        self.assertEqual(q(any='x'), [])
        self.assertEqual(q(artist='x'), [])
        self.assertEqual(q(album='x'), [])
        self.assertEqual(q(albumartist='x'), [])
        self.assertEqual(q(track_name='x'), [])

        self.assertEqual(q(any='foo'), [self.tracks['foo']])
        self.assertEqual(q(artist='foo'), [self.tracks['foo']])
        self.assertEqual(q(album='foo'), [self.tracks['foo']])
        self.assertEqual(q(albumartist='foo'), [self.tracks['foo']])
        self.assertEqual(q(track_name='foo'), [self.tracks['foo']])

        self.assertItemsEqual(
            q(track_name='foo', artist='foo'),
            [self.tracks['foo']]
        )
        self.assertItemsEqual(
            q(track_name='foo', artist='bar'),
            []
        )
        self.assertItemsEqual(
            q(album='bar'),
            [self.tracks['bar'], self.tracks['BAR']]
        )
        self.assertItemsEqual(
            q(artist='bar'),
            [self.tracks['bar']]
        )
