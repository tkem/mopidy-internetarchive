from __future__ import unicode_literals

import os

from mopidy import config, ext

__version__ = '1.0.2'

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


class Extension(ext.Extension):

    dist_name = 'Mopidy-InternetArchive'
    ext_name = 'internetarchive'
    version = __version__

    def get_default_config(self):
        return config.read(os.path.join(os.path.dirname(__file__), 'ext.conf'))

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['base_url'] = config.String()
        schema['username'] = config.String(optional=True)
        schema['collections'] = config.List()
        schema['audio_formats'] = config.List()
        schema['image_formats'] = config.List()
        schema['browse_limit'] = config.Integer(minimum=1, optional=True)
        schema['browse_order'] = config.String(choices=SORT_FIELDS, optional=True)  # noqa
        schema['search_limit'] = config.Integer(minimum=1, optional=True)
        schema['search_order'] = config.String(choices=SORT_FIELDS, optional=True)  # noqa
        schema['exclude_collections'] = config.List(optional=True)
        schema['exclude_mediatypes'] = config.List(optional=True)
        schema['cache_size'] = config.Integer(minimum=1, optional=True)
        schema['cache_ttl'] = config.Integer(minimum=0, optional=True)
        schema['timeout'] = config.Integer(minimum=0, optional=True)

        # no longer used (for now)
        schema['bookmarks'] = config.Deprecated()
        schema['bookmarks_label'] = config.Deprecated()
        schema['browse_label'] = config.Deprecated()
        schema['excludes'] = config.Deprecated()
        schema['mediatypes'] = config.Deprecated()
        schema['sort_order'] = config.Deprecated()

        return schema

    def setup(self, registry):
        from .backend import InternetArchiveBackend
        registry.add('backend', InternetArchiveBackend)
