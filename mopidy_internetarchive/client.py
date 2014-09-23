from __future__ import unicode_literals

import collections
import requests

from urlparse import urljoin

BASE_URL = 'http://archive.org/'


class InternetArchiveClient(object):

    def __init__(self, base_url=BASE_URL, timeout=None):
        self._search_url = urljoin(base_url, '/advancedsearch.php')
        self._metadata_url = urljoin(base_url, '/metadata/')
        self._download_url = urljoin(base_url, '/download/')
        self._bookmarks_url = urljoin(base_url, '/bookmarks/')
        self._session = requests.Session()
        self._timeout = timeout

    def search(self, query, fields=None, sort=None, rows=None, start=None):
        response = self._session.get(self._search_url, params={
            'q': query,
            'fl[]': fields,
            'sort[]': sort,
            'rows': rows,
            'start': start,
            'output': 'json'
        }, timeout=self._timeout)
        if not response.content:
            raise self.SearchError(response.url)
        return self.SearchResult(response.json())

    def metadata(self, path):
        url = urljoin(self._metadata_url, path.lstrip('/'))
        response = self._session.get(url, timeout=self._timeout)
        data = response.json()

        if not data:
            raise LookupError('Internet Archive item %s not found' % path)
        elif 'error' in data:
            raise LookupError(data['error'])
        elif 'result' in data:
            return data['result']
        else:
            return data

    def bookmarks(self, username):
        url = urljoin(self._bookmarks_url, username + '?output=json')
        response = self._session.get(url, timeout=self._timeout)
        # requests for non-existant users yield text/xml response
        if response.headers['Content-Type'] != 'application/json':
            raise LookupError('Internet Archive user %s not found' % username)
        return response.json()

    def geturl(self, identifier, filename=None):
        if filename:
            return urljoin(self._download_url, identifier + '/' + filename)
        else:
            return urljoin(self._download_url, identifier + '/')

    class SearchResult(collections.Sequence):

        def __init__(self, result):
            self.query = result['responseHeader']['params']['q']
            self.rowcount = result['response']['numFound']
            self.docs = result['response']['docs']

        def __getitem__(self, key):
            return self.docs[key]

        def __len__(self):
            return len(self.docs)

        def __iter__(self):
            return iter(self.docs)

    class SearchError(Exception):

        pass
