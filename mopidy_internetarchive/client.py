from __future__ import unicode_literals

import collections
import logging
import requests
import uritools

BASE_URL = 'http://archive.org/'

logger = logging.getLogger(__name__)


class InternetArchiveClient(object):

    pykka_traversable = True

    def __init__(self, base_url=BASE_URL, retries=0, timeout=None):
        self.base_url = base_url
        self.retries = retries
        self.timeout = timeout
        self.session = requests.Session()

    def search(self, query, fields=None, sort=None, rows=None, start=None):
        response = self._get('/advancedsearch.php', params={
            'q': query,
            'fl[]': fields,
            'sort[]': sort,
            'rows': rows,
            'start': start,
            'output': 'json'
        })
        if response.content:
            return self.SearchResult(response.json())
        else:
            raise self.SearchError(response.url)

    def metadata(self, identifier):
        obj = self._get('/metadata/' + identifier).json()
        if not obj:
            raise LookupError('Internet Archive item %s not found' % identifier)  # noqa
        elif 'error' in obj:
            raise LookupError(obj['error'])
        elif 'result' in obj:
            return obj['result']
        else:
            return obj

    def bookmarks(self, username):
        response = self._get('/bookmarks/' + username, params={
            'output': 'json'
        })
        # requests for non-existant users yield text/xml response
        if response.headers.get('Content-Type') != 'application/json':
            raise LookupError('Internet Archive user %s not found' % username)
        return response.json()

    def geturl(self, identifier, filename=None):
        if filename:
            path = identifier + '/' + uritools.uriencode(filename)
        else:
            path = identifier + '/'
        return uritools.urijoin(self.base_url, '/download/' + path)

    def _get(self, path, params=None):
        url = uritools.urijoin(self.base_url, path)
        retries = self.retries
        timeout = self.timeout

        while True:
            try:
                return self.session.get(url, params=params, timeout=timeout)
            except requests.exceptions.ConnectionError as e:
                if not retries:
                    raise e
                logger.warn('Error connecting to the Internet Archive: %s', e)
                retries -= 1

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
