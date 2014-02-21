from __future__ import unicode_literals

import datetime
import logging
import re

from mopidy.models import Artist

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

ISODATE_RE = re.compile(r"""
(\d{4})
(?:\-(\d{2}))?
(?:\-(\d{2}))?
""", flags=re.VERBOSE)

logger = logging.getLogger(__name__)


def parse_bitrate(bitrate, default=None):
    if not bitrate:
        return default
    try:
        return int(float(bitrate))
    except Exception:
        logger.warn('Invalid Internet Archive bitrate: %r', bitrate)
        return default


def parse_creator(creator, default=[]):
    if not creator:
        return default
    try:
        if isinstance(creator, basestring):
            creator = [creator]
        return [Artist(name=s.strip()) for s in creator]
    except Exception:
        logger.warn('Invalid Internet Archive creator: %r', creator)
        return default


def parse_date(date, default=None):
    if not date:
        return default
    try:
        return '-'.join(ISODATE_RE.match(date).groups('01'))
    except Exception:
        logger.warn('Invalid Internet Archive date: %r', date)
        return default


def parse_length(length, default=None):
    if not length:
        return default
    try:
        groups = DURATION_RE.match(length).groupdict('0')
    except Exception:
        logger.warn('Invalid Internet Archive length: %r', length)
        return default
    d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
    return int(d.total_seconds() * 1000)


def parse_mtime(mtime, default=None):
    if not mtime:
        return default
    try:
        return int(mtime)
    except Exception:
        logger.warn('Invalid Internet Archive mtime: %r', mtime)
        return default


def parse_title(title, default=None, ref=False):
    if not title or title == 'tmp':
        title = default
    if title and ref:
        return title.replace('/', '_')
    else:
        return title


def parse_track(track, default=None):
    if not track:
        return default
    try:
        return int(track.partition('/')[0])
    except Exception:
        logger.warn('Invalid Internet Archive track no.: %r', track)
        return default
