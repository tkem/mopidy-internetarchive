from __future__ import unicode_literals

import collections

import mock

import mopidy_internetarchive as ext

import pytest


@pytest.fixture
def config():
    return {
        'internetarchive': {
            'base_url': 'http://archive.org',
            'collections': ('audio', 'etree', 'foo'),
            'audio_formats': ('Flac', 'VBR MP3'),
            'image_formats': ('JPEG', 'PNG'),
            'browse_limit': None,
            'browse_views': collections.OrderedDict([
                ('title asc', 'Title'),
                ('creator asc', 'Creator')
            ]),
            'search_limit': None,
            'search_order': None,
            'cache_size': None,
            'cache_ttl': None,
            'retries': 0,
            'timeout': None
        },
        'proxy': {
        }
    }


@pytest.fixture
def root_collections():
    from mopidy.models import Ref
    return [
        Ref.directory(name='Audio Archive', uri='internetarchive:audio'),
        Ref.directory(name='Live Music Archive', uri='internetarchive:etree')
    ]


@pytest.fixture
def audio_mock():
    audio_mock = mock.Mock()
    return audio_mock


@pytest.fixture
def client_mock():
    client_mock = mock.Mock(spec=ext.client.InternetArchiveClient)
    client_mock.SearchResult = ext.client.InternetArchiveClient.SearchResult
    client_mock.cache = mock.Mock(spec=dict)
    client_mock.search.return_value = client_mock.SearchResult({
        'responseHeader': {
            'params': {
                'q': 'album'
            }
        },
        'response': {
            'numFound': 2,
            'docs': [{
                'identifier': 'etree',
                'title': 'Live Music Archive',
                'mediatype': 'collection'
            }, {
                'identifier': 'audio',
                'title': 'Audio Archive',
                'mediatype': 'collection'
            }]
        }
    })
    return client_mock


@pytest.fixture
def backend_mock(client_mock, config):
    backend_mock = mock.Mock(spec=ext.backend.InternetArchiveBackend)
    backend_mock.client = client_mock
    return backend_mock


@pytest.fixture
def library(backend_mock, config):
    return ext.library.InternetArchiveLibraryProvider(
        config['internetarchive'], backend_mock
    )


@pytest.fixture
def playback(audio_mock, backend_mock):
    return ext.playback.InternetArchivePlaybackProvider(
        audio_mock, backend_mock
    )
