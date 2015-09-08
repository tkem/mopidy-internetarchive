from __future__ import unicode_literals

import unittest

from mopidy.models import Artist

from mopidy_internetarchive import translator


class TranslatorTest(unittest.TestCase):

    def test_parse_bitrate(self):
        self.assertEqual(translator.parse_bitrate(None), None)
        self.assertEqual(translator.parse_bitrate(''), None)
        self.assertEqual(translator.parse_bitrate([]), None)
        self.assertEqual(translator.parse_bitrate('tmp'), None)

        self.assertEqual(translator.parse_bitrate(None, 42), 42)
        self.assertEqual(translator.parse_bitrate('', 42), 42)
        self.assertEqual(translator.parse_bitrate([], 42), 42)
        self.assertEqual(translator.parse_bitrate('tmp', 42), 42)

        self.assertEqual(translator.parse_bitrate('0'), 0)
        self.assertEqual(translator.parse_bitrate('1'), 1)
        self.assertEqual(translator.parse_bitrate('42.123'), 42)

    def test_parse_date(self):
        self.assertEqual(translator.parse_date(None), None)
        self.assertEqual(translator.parse_date(''), None)
        self.assertEqual(translator.parse_date([]), None)
        self.assertEqual(translator.parse_date('tmp'), None)

        self.assertEqual(translator.parse_date(None, 42), 42)
        self.assertEqual(translator.parse_date('', 42), 42)
        self.assertEqual(translator.parse_date([], 42), 42)
        self.assertEqual(translator.parse_date('tmp', 42), 42)

        self.assertEqual(
            translator.parse_date('2014-02-21T06:00:00Z'), '2014-02-21'
        )
        self.assertEqual(translator.parse_date('2014-02-21'), '2014-02-21')
        self.assertEqual(translator.parse_date('2014-02'), '2014-02-01')
        self.assertEqual(translator.parse_date('2014'), '2014-01-01')

    def test_parse_length(self):
        self.assertEqual(translator.parse_length(None), None)
        self.assertEqual(translator.parse_length(''), None)
        self.assertEqual(translator.parse_length([]), None)
        self.assertEqual(translator.parse_length('tmp'), None)

        self.assertEqual(translator.parse_length(None, 42), 42)
        self.assertEqual(translator.parse_length('', 42), 42)
        self.assertEqual(translator.parse_length([], 42), 42)
        self.assertEqual(translator.parse_length('tmp', 42), 42)

        self.assertEqual(translator.parse_length('0'), 0)
        self.assertEqual(translator.parse_length('1'), 1 * 1000)
        self.assertEqual(translator.parse_length('60'), 60 * 1000)
        self.assertEqual(translator.parse_length('1:00'), 60 * 1000)
        self.assertEqual(translator.parse_length('60:00'), 3600 * 1000)
        self.assertEqual(translator.parse_length('1:00:00'), 3600 * 1000)

    def test_parse_mtime(self):
        self.assertEqual(translator.parse_mtime(None), None)
        self.assertEqual(translator.parse_mtime(''), None)
        self.assertEqual(translator.parse_mtime([]), None)
        self.assertEqual(translator.parse_mtime('tmp'), None)

        self.assertEqual(translator.parse_mtime(None, 42), 42)
        self.assertEqual(translator.parse_mtime('', 42), 42)
        self.assertEqual(translator.parse_mtime([], 42), 42)
        self.assertEqual(translator.parse_mtime('tmp', 42), 42)

        self.assertEqual(translator.parse_mtime('0'), 0)
        self.assertEqual(translator.parse_mtime('1'), 1)

    def test_parse_track(self):
        self.assertEqual(translator.parse_track(None), None)
        self.assertEqual(translator.parse_track(''), None)
        self.assertEqual(translator.parse_track([]), None)
        self.assertEqual(translator.parse_track('tmp'), None)

        self.assertEqual(translator.parse_track(None, 42), 42)
        self.assertEqual(translator.parse_track('', 42), 42)
        self.assertEqual(translator.parse_track([], 42), 42)
        self.assertEqual(translator.parse_track('tmp', 42), 42)

        self.assertEqual(translator.parse_track('0'), 0)
        self.assertEqual(translator.parse_track('1'), 1)
        self.assertEqual(translator.parse_track('1/100'), 1)
        self.assertEqual(translator.parse_track('1/tmp'), 1)

    def test_parse_creator(self):
        artist = Artist(name='foo')

        self.assertEqual(translator.parse_creator(None), None)
        self.assertEqual(translator.parse_creator(''), None)
        self.assertEqual(translator.parse_creator([]), None)
        self.assertEqual(translator.parse_creator('tmp'), None)

        self.assertEqual(translator.parse_creator(None, [artist]), [artist])
        self.assertEqual(translator.parse_creator('', [artist]), [artist])
        self.assertEqual(translator.parse_creator([], [artist]), [artist])
        self.assertEqual(translator.parse_creator('tmp', [artist]), [artist])

        self.assertEqual(translator.parse_creator('foo'), [artist])
        self.assertEqual(translator.parse_creator(['foo']), [artist])
        self.assertEqual(translator.parse_creator(
            ['foo', 'foo']), [artist, artist]
        )
