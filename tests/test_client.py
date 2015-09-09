from __future__ import unicode_literals

import unittest

from mopidy_internetarchive.client import InternetArchiveClient


class ClientTest(unittest.TestCase):

    def test_useragent(self):
        client = InternetArchiveClient()
        self.assertIsNotNone(client.useragent)
        client.useragent = 'foobar/1.0'
        self.assertEqual(client.useragent, 'foobar/1.0')

    def test_proxies(self):
        client = InternetArchiveClient()
        self.assertIsNotNone(client.proxies)
        client.proxies['http'] = 'foo.bar:3128'
        self.assertEqual(client.proxies['http'], 'foo.bar:3128')
        client.proxies['https'] = 'foo.bar:4012'
        self.assertEqual(client.proxies['https'], 'foo.bar:4012')
