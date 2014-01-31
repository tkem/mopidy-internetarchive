from __future__ import unicode_literals

import re

from mopidy.models import Track, Album, Artist, Ref
from .uritools import uricompose

ISODATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

URI_SCHEME = 'internetarchive'


def item_to_tracks(item, files):
    metadata = item['metadata']
    identifier = metadata['identifier']
    album = doc_to_album(metadata)
    byname = {f['name']: f for f in item['files']}

    tracks = []
    for f in files:
        if 'original' in f and f['original'] in byname:
            orig = byname[f['original']]
            for key in orig:
                if not key in f or f[key] in ('', 'tmp'):
                    f[key] = orig[key]

        tracks.append(Track(
            uri=uricompose(URI_SCHEME, path=identifier, fragment=f['name']),
            name=f.get('title', f['name']),
            artists=parse_creator(f.get('creator'), album.artists),
            album=album,
            track_no=parse_track(f.get('track')),
            date=parse_date(f.get('date'), album.date),
            length=parse_length(f.get('length')),
            bitrate=parse_bitrate(f.get('bitrate')),
            last_modified=parse_mtime(f.get('mtime'))
        ))
    return tracks


def file_to_ref(item, file):
    identifier = item['metadata']['identifier']
    name = file.get('title', file['name'])  # FIXME: orig title?
    uri = uricompose(URI_SCHEME, path=identifier, fragment=file['name'])
    return Ref.track(uri=uri, name=name)


def doc_to_ref(doc, type=None):
    identifier = doc['identifier']
    name = doc.get('title', identifier)  # FIXME: title w/slashes?
    uri = uricompose(URI_SCHEME, path=identifier)
    if type is not None:
        return Ref(uri=uri, name=name, type=type)
    elif doc['mediatype'] == 'audio':
        return Ref.album(uri=uri, name=name)
    elif doc['mediatype'] == 'collection':
        return Ref.directory(uri=uri, name=name)
    else:
        return None


def doc_to_album(doc):
    identifier = doc['identifier']
    return Album(
        uri=uricompose(URI_SCHEME, path=identifier),
        name=doc.get('title', identifier),
        artists=parse_creator(doc.get('creator')),
        date=parse_date(doc.get('date'))
    )


def parse_creator(values, default=[]):
    if not values:
        return default
    if not hasattr(values, '__iter__'):
        values = [values]
    return [Artist(name=s) for s in values]


def parse_track(s, default=None):
    return int(s) if s else default


def parse_length(s, default=None):
    if not s:
        return default
    hms = (list(reversed(s.split(':', 2))) + [0, 0])[0:3]
    return int((float(hms[0]) + int(hms[1]) * 60 + int(hms[2]) * 3600) * 1000)


def parse_bitrate(s, default=None):
    return int(float(s)) if s else default


def parse_mtime(s, default=None):
    return int(s) if s else default


def parse_date(s, default=None):
    match = ISODATE_RE.match(s or '')
    if match:
        return '-'.join(match.groups())
    else:
        return default
