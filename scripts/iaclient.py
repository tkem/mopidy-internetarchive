from __future__ import unicode_literals

import argparse
import logging
import json
import sys

from mopidy_internetarchive.client import InternetArchiveClient

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
parser.add_argument('-S', '--sort', nargs='+')
parser.add_argument('-t', '--timeout', type=float)
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARN)

client = InternetArchiveClient(args.base_url, timeout=args.timeout)

if args.query:
    query = args.arg.decode(args.encoding)
    result = client.search(query, args.fields, args.sort, args.rows)
elif args.bookmarks:
    result = client.bookmarks(args.arg)
else:
    result = client.metadata(args.arg)

json.dump(result, sys.stdout, default=vars, indent=args.indent)
sys.stdout.write('\n')
