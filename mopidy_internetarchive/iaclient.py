from __future__ import unicode_literals

import collections
import logging
import re
import requests

from urlparse import urlsplit, urljoin

BASE_URL = 'http://archive.org/'

logger = logging.getLogger(__name__)


def cachedmethod(method):
    def makekey(args, kwargs):
        return (method.__name__, tuple(sorted(kwargs.items()))) + args

    def wrapper(self, *args, **kwargs):
        if self.cache is not None:
            key = makekey(args, kwargs)
            try:
                result = self.cache[key]
                logger.debug("cache hit: %s", key)
                return result
            except KeyError:
                logger.debug("cache miss: %s", key)
                result = method(self, *args, **kwargs)
                self.cache[key] = result
                return result
            except TypeError:
                logger.warn("cache fail: %s", key)
        return method(self, *args, **kwargs)
    return wrapper


class InternetArchiveClient(object):

    SPECIAL_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')

    def __init__(self, base_url=BASE_URL, timeout=None, cache=None):
        self.search_url = urljoin(base_url, '/advancedsearch.php')
        self.metadata_url = urljoin(base_url, '/metadata/')
        self.download_url = urljoin(base_url, '/download/')
        self.bookmarks_url = urljoin(base_url, '/bookmarks/')
        self.session = requests.Session()
        self.timeout = timeout
        self.cache = cache

    @cachedmethod
    def search(self, query, fields=None, sort=None, rows=None, start=None):
        response = self.session.get(self.search_url, params={
            'q': query,
            'fl[]': fields,
            'sort[]': sort,
            'rows': rows,
            'start': start,
            'output': 'json'
        }, timeout=self.timeout)
        if not response.content:
            raise self.SearchError(urlsplit(response.url).query)
        return self.SearchResult(response.json())

    @cachedmethod
    def metadata(self, path):
        url = urljoin(self.metadata_url, path.lstrip('/'))
        response = self.session.get(url, timeout=self.timeout)
        data = response.json()

        if not data:
            raise LookupError('Internet Archive item %r not found' % path)
        elif 'error' in data:
            raise LookupError(data['error'])
        elif 'result' in data:
            return data['result']
        else:
            return data

    @cachedmethod
    def bookmarks(self, username):
        url = urljoin(self.bookmarks_url, username) + '?output=json'
        response = self.session.get(url, timeout=self.timeout)
        # requests for non-existant users yield text/xml response
        if response.headers['Content-Type'] != 'application/json':
            raise LookupError('User account %r not found' % username)
        return response.json()

    def geturl(self, identifier, filename=None):
        if filename:
            return urljoin(self.download_url, identifier + '/' + filename)
        else:
            return urljoin(self.download_url, identifier + '/')

    @classmethod
    def query_string(cls, query, op=None, group=None):
        terms = []
        for (field, values) in query.iteritems():
            if not hasattr(values, '__iter__'):
                values = [values]
            values = [cls.quote_term(value) for value in values]
            if len(values) == 1:
                term = values[0]
            elif group:
                term = '(%s)' % (' ' + group + ' ').join(values)
            else:
                term = '(%s)' % ' '.join(values)
            terms.append(field + ':' + term if field else term)
        return (' ' + op + ' ' if op else ' ').join(terms)

    @classmethod
    def quote_term(cls, term):
        term = cls.SPECIAL_CHAR_RE.sub(r'\\\1', term)
        # only quote if term contains whitespace, since
        # date:"2014-01-01" will raise an error
        if any(c.isspace() for c in term):
            term = '"' + term + '"'
        return term

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

        def __init__(self, query):
            msg = 'Invalid Internet Archive query %r' % query
            super(InternetArchiveClient.SearchError, self).__init__(msg)


if __name__ == '__main__':
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('arg', metavar='PATH | USER | QUERY')
    parser.add_argument('-B', '--base', default='http://archive.org')
    parser.add_argument('-b', '--bookmarks', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--encoding', default=sys.getdefaultencoding())
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-i', '--indent', type=int, default=2)
    parser.add_argument('-q', '--query', action='store_true')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-s', '--sort', nargs='+')
    parser.add_argument('-S', '--start', type=int)
    parser.add_argument('-t', '--timeout', type=float)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    client = InternetArchiveClient(args.base, timeout=args.timeout)

    if args.query:
        query = args.arg.decode(args.encoding)
        if query.startswith('{'):
            query = client.query_string(eval(query))
        result = client.search(query, args.fields, args.sort, args.rows,
                               args.start)
    elif args.bookmarks:
        result = client.bookmarks(args.arg)
    else:
        result = client.metadata(args.arg)

    json.dump(result, sys.stdout, default=vars, indent=args.indent)
    sys.stdout.write('\n')
