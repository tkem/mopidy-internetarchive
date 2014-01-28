from __future__ import unicode_literals

import re

from mopidy.models import Track, Album, Artist, Ref
from .uritools import uricompose

ISODATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

URI_SCHEME = 'internetarchive'


def item_to_tracks(item, files):
    metadata = item['metadata']
    id = metadata['identifier']
    album = metadata_to_album(metadata)
    byname = {f['name']: f for f in item['files']}

    tracks = []
    for file in files:
        if 'original' in file and file['original'] in byname:
            orig = byname[file['original']]
            for key in orig:
                if not key in file or file[key] in ('', 'tmp'):
                    file[key] = orig[key]

        track = Track(
            uri=uricompose(URI_SCHEME, path=id, fragment=file['name']),
            name=file.get('title', file['name']),
            artists=parse_creator(file.get('creator'), album.artists),
            album=album,
            track_no=parse_track(file.get('track')),
            date=parse_date(file.get('date'), album.date),
            length=parse_length(file.get('length')),
            bitrate=parse_bitrate(file.get('bitrate')),
            last_modified=parse_mtime(file.get('mtime'))
        )
        tracks.append(track)
    return tracks


def file_to_ref(item, f):
    id = item['metadata']['identifier']
    uri = uricompose(URI_SCHEME, path=id, fragment=f['name'])
    name = f.get('title', f['name'])  # TODO: orig title?
    return Ref.track(uri=uri, name=name)


def metadata_to_ref(metadata, type=None):
    id = metadata['identifier']
    uri = uricompose(URI_SCHEME, path=id)
    name = metadata.get('title', id)
    name = id  # FIXME: check for title w/spaces or slashes
    if type is not None:
        return Ref(uri=uri, name=name, type=type)
    elif metadata['mediatype'] == 'audio':
        return Ref.album(uri=uri, name=name)
    elif metadata['mediatype'] == 'collection':
        return Ref.directory(uri=uri, name=name)
    else:
        return None


def metadata_to_album(metadata):
    id = metadata['identifier']
    return Album(
        uri=uricompose(URI_SCHEME, path=id),
        name=metadata.get('title', id),
        artists=parse_creator(metadata.get('creator')),
        date=parse_date(metadata.get('date'))
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
