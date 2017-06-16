from __future__ import unicode_literals

import collections
import operator
import urlparse

import cachetools

import requests

BASE_URL = 'http://archive.org/'


def _session(base_url, retries):
    # TODO: backoff?
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session.mount(base_url, adapter)
    return session


class InternetArchiveClient(object):

    pykka_traversable = True

    def __init__(self, base_url=BASE_URL, retries=0, timeout=None):
        self.__base_url = base_url
        self.__session = _session(base_url, retries)
        self.__timeout = timeout
        self.cache = None  # public

    @property
    def proxies(self):
        return self.__session.proxies

    @property
    def useragent(self):
        return self.__session.headers.get('User-Agent')

    @useragent.setter
    def useragent(self, value):
        self.__session.headers['User-Agent'] = value

    @cachetools.cachedmethod(operator.attrgetter('cache'))
    def getitem(self, identifier):
        obj = self.__get('/metadata/%s' % identifier).json()
        if not obj:
            raise LookupError(identifier)
        elif 'error' in obj:
            raise LookupError(obj['error'])
        elif 'result' in obj:
            return obj['result']
        else:
            return obj

    def geturl(self, identifier, filename=None):
        if filename:
            path = '/download/%s/%s' % (identifier, filename)
        else:
            path = '/download/%s' % identifier
        return urlparse.urljoin(self.__base_url, path)

    def search(self, query, fields=None, sort=None, rows=None, start=None):
        response = self.__get('/advancedsearch.php', params={
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

    def __get(self, path, params=None):
        return self.__session.get(
            urlparse.urljoin(self.__base_url, path),
            params=params,
            timeout=self.__timeout
        )

    class SearchResult(collections.Sequence):

        def __init__(self, result):
            response = result['response']
            self.docs = response.get('docs', [])
            self.rowcount = response.get('numFound', None)
            # query is optional, and responseHeader likely to change
            try:
                self.query = result['responseHeader']['params']['query']
            except:
                self.query = None

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
    parser.add_argument('-B', '--base-url', default='http://archive.org')
    parser.add_argument('-e', '--encoding', default=sys.getdefaultencoding())
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-i', '--indent', type=int, default=2)
    parser.add_argument('-q', '--query', action='store_true')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-R', '--retries', type=int, default=0)
    parser.add_argument('-s', '--sort', nargs='+')
    parser.add_argument('-t', '--timeout', type=float)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARN)

    client = InternetArchiveClient(args.base_url, args.retries, args.timeout)
    if args.query:
        query = args.arg.decode(args.encoding)
        result = client.search(query, args.fields, args.sort, args.rows)
    else:
        result = client.getitem(args.arg)
    json.dump(result, sys.stdout, default=vars, indent=args.indent)
    sys.stdout.write('\n')
