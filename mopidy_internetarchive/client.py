from __future__ import unicode_literals
import logging
import requests

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

    def __init__(self, base_url='http://archive.org', cache=None):
        self.search_url = base_url + '/advancedsearch.php'
        self.metadata_url = base_url + '/metadata'
        self.download_url = base_url + '/download'
        self.session = requests.Session()  # TODO: timeout, etc.
        self.cache = cache

    @cachedmethod
    def search(self, query, fields=[], sort=[], rows=None, start=None):
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

    class SearchResult(object):

        def __init__(self, result):
            self.query = result['responseHeader']['params']['q']
            self.num_found = result['response']['numFound']
            self.start = result['response']['start']
            self.docs = result['response']['docs']

        def __len__(self):
            return len(self.docs)

        def __iter__(self):
            return iter(self.docs)

        def __repr__(self):
            fields = []
            for (key, value) in sorted(self.__dict__.items()):
            #    if isinstance(value, (frozenset, tuple)):
            #        value = list(value)
                fields.append('%s=%s' % (key, repr(value)))
            return '%s(%s)' % (self.__class__.__name__, ', '.join(fields))

    class SearchError(Exception):

        def __init__(self, query):
            msg = 'Invalid query: ' + query
            super(InternetArchiveClient.SearchError, self).__init__(msg)


if __name__ == '__main__':
    import argparse
    import json
    import sys

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', nargs='?')
    parser.add_argument('-b', '--base-url', default='http://archive.org')
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-q', '--query')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-s', '--sort', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--start', type=int)
    args = parser.parse_args()

    client = InternetArchiveClient(args.base_url)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.path:
        result = client.getitem(args.path)
    else:
        result = client.search(
            args.query, args.fields, args.sort, args.rows, args.start
        )
    json.dump(result, sys.stdout, default=vars, indent=2)
    sys.stdout.write('\n')
