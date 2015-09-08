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

if __name__ == '__main__':
    import argparse
    import logging
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('arg', metavar='PATH | USER | QUERY')
    parser.add_argument('-b', '--bookmarks', action='store_true')
    parser.add_argument('-B', '--base-url', default='http://archive.org')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--encoding', default=sys.getdefaultencoding())
    parser.add_argument('-F', '--fields', nargs='+')
    parser.add_argument('-i', '--indent', type=int, default=2)
    parser.add_argument('-q', '--query', action='store_true')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-R', '--retries', type=int, default=0)
    parser.add_argument('-S', '--sort', nargs='+')
    parser.add_argument('-t', '--timeout', type=float)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARN)

    client = InternetArchiveClient(
        args.base_url,
        retries=args.retries,
        timeout=args.timeout
    )

    if args.query:
        query = args.arg.decode(args.encoding)
        result = client.search(query, args.fields, args.sort, args.rows)
    elif args.bookmarks:
        result = client.bookmarks(args.arg)
    else:
        result = client.metadata(args.arg)

    json.dump(result, sys.stdout, default=vars, indent=args.indent)
    sys.stdout.write('\n')
