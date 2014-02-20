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

ISODATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

logger = logging.getLogger(__name__)


def parse_bitrate(value, default=None):
    if not value:
        return default
    try:
        return int(float(value))
    except Exception:
        logger.warn('Invalid Internet Archive bitrate: %r', value)
        return default


def parse_creator(value, default=[]):
    if not value:
        return default
    try:
        if isinstance(value, basestring):
            value = [value]
        return [Artist(name=s.strip()) for s in value]
    except Exception:
        logger.warn('Invalid Internet Archive creator: %r', value)
        return default


def parse_date(value, default=None):
    if not value:
        return default
    try:
        return ISODATE_RE.match(value).group()
    except Exception:
        logger.warn('Invalid Internet Archive date: %r', value)
        return default


def parse_length(value, default=None):
    if not value:
        return default
    try:
        groups = DURATION_RE.match(value).groupdict('0')
    except Exception:
        logger.warn('Invalid Internet Archive length: %r', value)
        return default
    d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
    return int(d.total_seconds() * 1000)


def parse_mtime(value, default=None):
    if not value:
        return default
    try:
        return int(value)
    except Exception:
        logger.warn('Invalid Internet Archive mtime: %r', value)
        return default


def parse_title(value, default=None):
    return value if value else default


def parse_track(value, default=None):
    if not value:
        return default
    try:
        return int(value.partition('/')[0])
    except Exception:
        logger.warn('Invalid Internet Archive track no.: %r', value)
        return default
