from __future__ import unicode_literals
import logging
import requests

logger = logging.getLogger('mopidy.backends.internetarchive.client')


class InternetArchiveClient(object):

    def __init__(self, base_url='http://archive.org'):
        self.search_url = base_url + '/advancedsearch.php'
        self.metadata_url = base_url + '/metadata/'
        self.download_url = base_url + '/download'
        self.session = requests.Session()  # TODO: timeout, etc.

    def search(self, query, fields=None, rows=None, start=None):
        response = self.session.get(self.search_url, params={
            'q': query,
            'fl[]': fields,
            'rows': rows,
            'start': start,
            'output': 'json'
        })
        logger.debug("URL: %s", response.url)
        return self.SearchResult(response)

    def metadata(self, path):
        url = self.metadata_url + path
        response = self.session.get(url)
        if not response.content:
            raise Exception('No content in response')
        # FIXME: unquote "\'", etc.
        return response.json()

    def get_item(self, identifier, *subitems):
        url = self.metadata_url + identifier + '/' + '/'.join(subitems)
        response = self.session.get(url)
        logger.debug("JSON: %s", repr(response))
        # FIXME: handle error/empty
        item = response.json()
        if 'result' in item:
            return item['result']
        else:
            return item

    def get_download_url(self, identifier, filename):
        return '%s/%s/%s' % (self.download_url, identifier, filename)

    class SearchResult(object):
        def __init__(self, response):
            if not response.content:
                raise Exception('No content in response')
            result = response.json()
            self.query = result['responseHeader']['params']['q']
            self.found = result['response']['numFound']
            self.start = result['response']['start']
            self.docs = result['response']['docs']

        def __len__(self):
            return len(self.docs)

        def __iter__(self):
            return iter(self.docs)

if __name__ == '__main__':
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', nargs='?')
    parser.add_argument('-b', '--base-url', default='http://archive.org')
    parser.add_argument('-f', '--fields', nargs='+')
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-s', '--start', type=int)
    parser.add_argument('-q', '--query')
    args = parser.parse_args()

    client = InternetArchiveClient(args.base_url)
    if args.path:
        result = client.metadata(args.path)
    else:
        result = client.search(args.query, args.fields, args.rows, args.start)
    json.dump(result, sys.stdout, default=vars, indent=2)
    sys.stdout.write('\n')
