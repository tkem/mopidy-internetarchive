from __future__ import unicode_literals
import unittest
import requests

from mopidy_internetarchive.client import InternetArchiveClient


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = InternetArchiveClient()

    def test_search(self):
        query = 'mediatype:audio creator:(Martin Luther King) title:(I Have a Dream) date:1963-08-28'
        result = self.client.search(query, fields=['identifier'])
        self.assertIn({'identifier': 'MLKDream'}, result.docs)

    def test_get_item(self):
        item = self.client.get_item('MLKDream')
        self.assertEqual(item['metadata']['identifier'], 'MLKDream')
        self.assertEqual(item['files_count'], len(item['files']))

    def test_get_metadata(self):
        metadata = self.client.get_item('MLKDream', 'metadata')
        self.assertEqual(metadata['identifier'], 'MLKDream')
        self.assertRegexpMatches(metadata['creator'], 'Martin Luther King')
        self.assertRegexpMatches(metadata['title'], 'I Have a Dream')
        self.assertRegexpMatches(metadata['date'], '1963-08-28')

    def test_get_download_url(self):
        for file in self.client.get_item('MLKDream', 'files'):
            url = self.client.get_download_url('MLKDream', file['name'])
            r = requests.head(url, allow_redirects=True)
            self.assertEqual(r.status_code, 200)
            if 'Content-Length' in r.headers and 'size' in file:
                self.assertEqual(r.headers['Content-Length'], file['size'])
