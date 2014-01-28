from __future__ import unicode_literals
import logging
import requests

logger = logging.getLogger(__name__)


class InternetArchiveClient(object):

    def __init__(self, base_url='http://archive.org', cache=None):
        self.search_url = base_url + '/advancedsearch.php'
        self.metadata_url = base_url + '/metadata'
        self.download_url = base_url + '/download'
        self.session = requests.Session()  # TODO: timeout, etc.
        self.cache = cache

    def search(self, query, fields=[], sort=[], rows=None, start=None):
        key = (query, frozenset(fields), tuple(sort), rows, start)
        if self.cache and key in self.cache:
            return self.cache[key]
        response = self.session.get(self.search_url, params={
            'q': query,
            'fl[]': fields,
            'sort[]': sort,
            'rows': rows,
            'start': start,
            'output': 'json'
        })
        logger.debug("search URL: %s", response.url)

        if not response.content:
            raise self.SearchError(query)
        result = self.SearchResult(response.json())
        if self.cache is not None:
            self.cache[key] = result
        return result

    def getitem(self, path):
        if self.cache and path in self.cache:
            return self.cache[path]
        url = '%s/%s' % (self.metadata_url, path)
        response = self.session.get(url)
        logger.debug("metadata URL: %s", response.url)

        data = response.json()
        # FIXME: cache errors?
        if not data or 'error' in data:
            return None
        # only subitems produce { "result": ... }
        if 'result' in data:
            data = data['result']
        if self.cache is not None:
            self.cache[path] = data
        return data

    def geturl(self, identifier, filename):
        return '%s/%s/%s' % (self.download_url, identifier, filename)

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

    class SearchError(Exception):

        def __init__(self, query):
            msg = 'Invalid query: ' + query
            super(InternetArchiveClient.SearchError, self).__init__(msg)


if __name__ == '__main__':
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', nargs='?')
    parser.add_argument('-b', '--base-url', default='http://archive.org')
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-s', '--sort', nargs='+')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-o', '--start', type=int)
    parser.add_argument('-q', '--query')
    args = parser.parse_args()

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    client = InternetArchiveClient(args.base_url)
    if args.path:
        result = client.getitem(args.path)
    else:
        result = client.search(args.query, args.fields, args.sort, args.rows, args.start)
    json.dump(result, sys.stdout, default=vars, indent=2)
    sys.stdout.write('\n')
