from __future__ import unicode_literals

import mock

from mopidy_internetarchive import Extension, backend


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert '[internetarchive]' in config
    assert 'enabled = true' in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert 'audio_formats' in schema
    assert 'base_url' in schema
    assert 'browse_limit' in schema
    assert 'browse_order' in schema
    assert 'cache_size' in schema
    assert 'cache_ttl' in schema
    assert 'collections' in schema
    assert 'exclude_collections' in schema
    assert 'exclude_mediatypes' in schema
    assert 'image_formats' in schema
    assert 'retries' in schema
    assert 'search_limit' in schema
    assert 'search_order' in schema
    assert 'timeout' in schema


def test_setup():
    registry = mock.Mock()

    ext = Extension()
    ext.setup(registry)

    registry.add.assert_called_with('backend', backend.InternetArchiveBackend)
