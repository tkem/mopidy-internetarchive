from __future__ import unicode_literals

import unittest

from mopidy.models import Artist
from mopidy_internetarchive.parsing import *  # noqa


class ParsingTest(unittest.TestCase):

    def test_parse_bitrate(self):
        self.assertEqual(parse_bitrate(None), None)
        self.assertEqual(parse_bitrate(''), None)
        self.assertEqual(parse_bitrate([]), None)
        self.assertEqual(parse_bitrate('tmp'), None)

        self.assertEqual(parse_bitrate(None, 42), 42)
        self.assertEqual(parse_bitrate('', 42), 42)
        self.assertEqual(parse_bitrate([], 42), 42)
        self.assertEqual(parse_bitrate('tmp', 42), 42)

        self.assertEqual(parse_bitrate('0'), 0)
        self.assertEqual(parse_bitrate('1'), 1)
        self.assertEqual(parse_bitrate('42.123'), 42)

    def test_parse_creator(self):
        ax, ay = Artist(name='x'), Artist(name='y')

        self.assertEqual(parse_creator(None), [])
        self.assertEqual(parse_creator(''), [])
        self.assertEqual(parse_creator([]), [])
        self.assertEqual(parse_creator([{}]), [])

        self.assertEqual(parse_creator(None, [ax]), [ax])
        self.assertEqual(parse_creator('', [ax]), [ax])
        self.assertEqual(parse_creator([], [ax]), [ax])
        self.assertEqual(parse_creator([{}], [ax]), [ax])

        self.assertEqual(parse_creator('x'), [ax])
        self.assertEqual(parse_creator(['x']), [ax])
        self.assertEqual(parse_creator(['x', 'y']), [ax, ay])

    def test_parse_date(self):
        self.assertEqual(parse_date(None), None)
        self.assertEqual(parse_date(''), None)
        self.assertEqual(parse_date([]), None)
        self.assertEqual(parse_date('tmp'), None)

        self.assertEqual(parse_date(None, 42), 42)
        self.assertEqual(parse_date('', 42), 42)
        self.assertEqual(parse_date([], 42), 42)
        self.assertEqual(parse_date('tmp', 42), 42)

        self.assertEqual(parse_date('2014-02-21T06:00:00Z'), '2014-02-21')
        self.assertEqual(parse_date('2014-02-21'), '2014-02-21')
        self.assertEqual(parse_date('2014-02'), '2014-02-01')
        self.assertEqual(parse_date('2014'), '2014-01-01')

    def test_parse_length(self):
        self.assertEqual(parse_length(None), None)
        self.assertEqual(parse_length(''), None)
        self.assertEqual(parse_length([]), None)
        self.assertEqual(parse_length('tmp'), None)

        self.assertEqual(parse_length(None, 42), 42)
        self.assertEqual(parse_length('', 42), 42)
        self.assertEqual(parse_length([], 42), 42)
        self.assertEqual(parse_length('tmp', 42), 42)

        self.assertEqual(parse_length('0'), 0)
        self.assertEqual(parse_length('1'), 1 * 1000)
        self.assertEqual(parse_length('60'), 60 * 1000)
        self.assertEqual(parse_length('1:00'), 60 * 1000)
        self.assertEqual(parse_length('60:00'), 3600 * 1000)
        self.assertEqual(parse_length('1:00:00'), 3600 * 1000)

    def test_parse_mtime(self):
        self.assertEqual(parse_mtime(None), None)
        self.assertEqual(parse_mtime(''), None)
        self.assertEqual(parse_mtime([]), None)
        self.assertEqual(parse_mtime('tmp'), None)

        self.assertEqual(parse_mtime(None, 42), 42)
        self.assertEqual(parse_mtime('', 42), 42)
        self.assertEqual(parse_mtime([], 42), 42)
        self.assertEqual(parse_mtime('tmp', 42), 42)

        self.assertEqual(parse_mtime('0'), 0)
        self.assertEqual(parse_mtime('1'), 1)

    def test_parse_title(self):
        self.assertEqual(parse_title(None), None)
        self.assertEqual(parse_title(''), None)
        self.assertEqual(parse_title([]), None)
        self.assertEqual(parse_title('tmp'), None)

        self.assertEqual(parse_title(None, 'x'), 'x')
        self.assertEqual(parse_title('', 'x'), 'x')
        self.assertEqual(parse_title([], 'x'), 'x')
        self.assertEqual(parse_title('tmp', 'x'), 'x')

        self.assertEqual(parse_title('x'), 'x')
        self.assertEqual(parse_title('x/y/z'), 'x/y/z')
        self.assertEqual(parse_title('x', ref=True), 'x')
        self.assertEqual(parse_title('x/y/z', ref=True), 'x_y_z')

    def test_parse_track(self):
        self.assertEqual(parse_track(None), None)
        self.assertEqual(parse_track(''), None)
        self.assertEqual(parse_track([]), None)
        self.assertEqual(parse_track('tmp'), None)

        self.assertEqual(parse_track(None, 42), 42)
        self.assertEqual(parse_track('', 42), 42)
        self.assertEqual(parse_track([], 42), 42)
        self.assertEqual(parse_track('tmp', 42), 42)

        self.assertEqual(parse_track('0'), 0)
        self.assertEqual(parse_track('1'), 1)
        self.assertEqual(parse_track('1/100'), 1)
        self.assertEqual(parse_track('1/tmp'), 1)
