from __future__ import unicode_literals

import unittest

from mopidy_internetarchive import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()
        self.assertIn('[internetarchive]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()
        self.assertIn('base_url', schema)
        self.assertIn('collections', schema)
        self.assertIn('audio_formats', schema)
        self.assertIn('image_formats', schema)
        self.assertIn('browse_limit', schema)
        self.assertIn('browse_order', schema)
        self.assertIn('search_limit', schema)
        self.assertIn('search_order', schema)
        self.assertIn('exclude_collections', schema)
        self.assertIn('exclude_mediatypes', schema)
        self.assertIn('cache_size', schema)
        self.assertIn('cache_ttl', schema)
        self.assertIn('retries', schema)
        self.assertIn('timeout', schema)
