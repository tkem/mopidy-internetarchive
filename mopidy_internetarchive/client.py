from __future__ import unicode_literals

import collections
import logging
import re
import requests

SPECIAL_CHAR_RE = re.compile(r'([+!(){}\[\]^"~*?:\\]|\&\&|\|\|)')

logger = logging.getLogger(__name__)


def _quote_term(term):
    term = SPECIAL_CHAR_RE.sub(r'\\\1', term)
    # only quote if term contains whitespace, since something like
    # date:"2014-01-01" will give an error
    if any(c.isspace() for c in term):
        term = '"' + term + '"'
    return term


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

    def __init__(self, base_url='http://archive.org/', cache=None):
        from urlparse import urljoin
        self.search_url = urljoin(base_url, '/advancedsearch.php')
        self.metadata_url = urljoin(base_url, '/metadata')
        self.download_url = urljoin(base_url, '/download')
        self.session = requests.Session()  # TODO: timeout, etc.
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
        })

        if not response.content:
            raise self.SearchError(query)
        return self.SearchResult(response.json())

    @cachedmethod
    def getitem(self, path):
        url = '%s/%s' % (self.metadata_url, path.strip('/'))
        response = self.session.get(url)
        data = response.json()

        if not data or 'error' in data:
            return None  # FIXME: cache errors?
        # only subitems produce { "result": ... }
        if 'result' in data:
            return data['result']
        else:
            return data

    def geturl(self, identifier, filename):
        return '%s/%s/%s' % (
            self.download_url, identifier.strip('/'), filename
        )

    def query_string(self, query):
        terms = []
        for (field, values) in query.iteritems():
            if not hasattr(values, '__iter__'):
                values = [values]
            values = [_quote_term(value) for value in values]
            if len(values) > 1:
                term = '(%s)' % ' OR '.join(values)
            else:
                term = values[0]
            terms.append(field + ':' + term if field else term)
        return ' '.join(terms)

    class SearchResult(collections.Sequence):

        def __init__(self, result):
            self.query = result['responseHeader']['params']['q']
            self.num_found = result['response']['numFound']
            self.start = result['response']['start']
            self.docs = result['response']['docs']

        def __getitem__(self, key):
            return self.docs.__getitem__(key)

        def __len__(self):
            return self.docs.__len__()

        def __iter__(self):
            return self.docs.__iter__()

    class SearchError(Exception):

        def __init__(self, query):
            msg = 'Invalid query: ' + query
            super(InternetArchiveClient.SearchError, self).__init__(msg)


if __name__ == '__main__':
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('arg', metavar='PATH | QUERY')
    parser.add_argument('-b', '--base-url', default='http://archive.org')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--encoding', default='utf-8')
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-i', '--indent', type=int, default=2)
    parser.add_argument('-q', '--query', action='store_true')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-s', '--sort', nargs='+')
    parser.add_argument('--start', type=int)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARN)

    client = InternetArchiveClient(args.base_url)
    if args.query:
        query = args.arg.decode(args.encoding)
        if query.startswith('{'):
            qs = client.query_string(eval(query))
        else:
            qs = query
        result = client.search(qs, args.fields, args.sort, args.rows, args.start)
    else:
        result = client.getitem(args.arg)
    json.dump(result, sys.stdout, default=vars, indent=args.indent)
    sys.stdout.write('\n')
