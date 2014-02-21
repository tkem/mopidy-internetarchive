from __future__ import unicode_literals

from mopidy import config, ext

__version__ = '0.3.1'

SORT_ORDER_CHOICES = ['%s %s' % (f, o) for o in ('asc', 'desc') for f in (
    'avg_rating',
    'creatorSorter'
    'date',
    'downloads',
    'month',
    'publicdate',
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
        import os
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['base_url'] = config.String()
        schema['collections'] = config.List()
        schema['mediatypes'] = config.List()
        schema['bookmarks'] = config.List(optional=True)
        schema['formats'] = config.List()
        schema['sort_order'] = config.String(choices=SORT_ORDER_CHOICES)
        schema['search_limit'] = config.Integer(minimum=1, optional=True)
        schema['browse_limit'] = config.Integer(minimum=1, optional=True)
        schema['browse_label'] = config.String()
        schema['bookmarks_label'] = config.String()
        schema['cache_size'] = config.Integer(minimum=1)
        schema['cache_ttl'] = config.Integer(minimum=1)
        schema['timeout'] = config.Integer(minimum=0, optional=True)
        return schema

    def setup(self, registry):
        from .backend import InternetArchiveBackend
        registry.add('backend', InternetArchiveBackend)
