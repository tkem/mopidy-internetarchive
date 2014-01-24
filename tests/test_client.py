from __future__ import unicode_literals
import unittest
import requests

from mopidy_internetarchive.client import InternetArchiveClient


TEST_QUERY = """
mediatype:audio
AND creator:(Martin Luther King)
AND title:"I Have a Dream"
AND date:1963-08-28
"""


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = InternetArchiveClient()

    def test_search(self):
        result = self.client.search(TEST_QUERY, fields=['identifier'])
        self.assertIn({'identifier': 'MLKDream'}, result.docs)

    def test_get_item(self):
        item = self.client.metadata('MLKDream')
        self.assertEqual(item['metadata']['identifier'], 'MLKDream')
        self.assertEqual(item['files_count'], len(item['files']))

    def test_get_metadata(self):
        metadata = self.client.metadata('MLKDream/metadata')
        self.assertEqual(metadata['identifier'], 'MLKDream')
        self.assertRegexpMatches(metadata['creator'], 'Martin Luther King')
        self.assertRegexpMatches(metadata['title'], 'I Have a Dream')
        self.assertRegexpMatches(metadata['date'], '1963-08-28')

    def test_get_download_url(self):
        for f in self.client.metadata('MLKDream/files'):
            url = self.client.get_download_url('MLKDream', f['name'])
            response = requests.head(url, allow_redirects=True)
            self.assertEqual(response.status_code, 200)
