from __future__ import unicode_literals

import collections
import os

from mopidy import config, ext

__version__ = '2.0.3'

SORT_FIELDS = ['%s %s' % (f, o) for o in ('asc', 'desc') for f in (
    'addeddate',
    'avg_rating',
    'call_number',
    'createdate',
    'creatorSorter',
    'date',
    'downloads',
    'foldoutcount',
    'headerImage',
    'identifier',
    'imagecount',
    'indexdate',
    'languageSorter',
    'licenseurl',
    'month',
    'nav_order',
    'num_reviews',
    'publicdate',
    'reviewdate',
    'stars',
    'titleSorter',
    'week',
    'year'
)]


class ConfigMap(config.ConfigValue):

    def __init__(self, keys=config.String(), values=config.String(), delim='|',
                 optional=False):
        self.__keys = keys
        self.__values = values
        self.__delim = delim
        self.__optional = optional

    def deserialize(self, value):
        dict = collections.OrderedDict()
        for s in config.List(optional=self.__optional).deserialize(value):
            parts = s.partition(self.__delim)
            key = self.__keys.deserialize(parts[0])
            val = self.__values.deserialize(parts[2])
            dict[key] = val
        return dict

    def serialize(self, value, display=False):
        if not value:
            return b''
        items = [
            (self.__keys.serialize(k), self.__values.serialize(v))
            for k, v in value.items()
        ]
        return config.List().serialize(map(self.__delim.join, items))


class Extension(ext.Extension):

    dist_name = 'Mopidy-InternetArchive'
    ext_name = 'internetarchive'
    version = __version__

    def get_default_config(self):
        return config.read(os.path.join(os.path.dirname(__file__), 'ext.conf'))

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema.update(
            base_url=config.String(),
            collections=config.List(),
            audio_formats=config.List(),
            image_formats=config.List(),
            browse_limit=config.Integer(minimum=1, optional=True),
            browse_views=ConfigMap(keys=config.String(choices=SORT_FIELDS)),
            search_limit=config.Integer(minimum=1, optional=True),
            search_order=config.String(choices=SORT_FIELDS, optional=True),
            cache_size=config.Integer(minimum=1, optional=True),
            cache_ttl=config.Integer(minimum=0, optional=True),
            retries=config.Integer(minimum=0),
            timeout=config.Integer(minimum=0, optional=True),
            # no longer used
            browse_order=config.Deprecated(),
            exclude_collections=config.Deprecated(),
            exclude_mediatypes=config.Deprecated(),
            username=config.Deprecated()
        )
        return schema

    def setup(self, registry):
        from .backend import InternetArchiveBackend
        registry.add('backend', InternetArchiveBackend)
