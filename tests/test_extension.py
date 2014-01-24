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
        self.assertIn('collection', schema)
        self.assertIn('mediatype', schema)
        self.assertIn('format', schema)
