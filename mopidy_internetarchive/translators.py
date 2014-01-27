from __future__ import unicode_literals

import re

from datetime import date

from mopidy.models import Track, Album, Artist, Ref

ISODATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def creator_to_artists(creator):
    if not creator:
        return None
    if not hasattr(creator, '__iter__'):
        creator = [creator]
    return [creator_to_artist(i) for i in creator]


def creator_to_artist(creator):
    if creator is None:
        return None
    else:
        return Artist(name=creator)


def parse_length(length):
    if not length:
        return None
    hms = (list(reversed(length.split(':', 2))) + [0, 0])[0:3]
    return int((float(hms[0]) + int(hms[1]) * 60 + int(hms[2]) * 3600) * 1000)


def parse_date(s):
    if not s:
        return None
    match = ISODATE_RE.match(s)
    if match:
        return date(*(int(i) for i in ISODATE_RE.match(s).groups())).isoformat()
    else:
        return None
