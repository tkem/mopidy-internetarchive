from __future__ import unicode_literals
import unittest

from mopidy_internetarchive.backend import InternetArchiveBackend


class BackendTest(unittest.TestCase):
    config = {
        'internetarchive': {
            'base_url': 'http://archive.org',
            'collections': ['etree', 'audio'],
            'mediatypes': ['etree', 'audio'],
            'formats': ['MP3']
        }
    }

    def setUp(self):
        self.backend = InternetArchiveBackend(config=self.config, audio=None)
