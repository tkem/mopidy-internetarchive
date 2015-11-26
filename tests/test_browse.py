from __future__ import unicode_literals

from mopidy import models

COLLECTION = {
    'metadata': {
        'identifier': 'directory',
        'title': 'Directory',
        'mediatype': 'collection'
    }
}

ITEM = {
    'files': [{
        'name': 'track02.mp3',
        'title': 'Track #2',
        'format': 'VBR MP3',
        'track': '02'
    }, {
        'name': 'track01.mp3',
        'title': 'Track #1',
        'format': 'VBR MP3',
        'track': '01'
    }],
    'metadata': {
        'identifier': 'album',
        'title': 'Album',
        'mediatype': 'audio'
    }
}

TRACKS = [
    models.Ref.track(name='Track #1', uri='internetarchive:album#track01.mp3'),
    models.Ref.track(name='Track #2', uri='internetarchive:album#track02.mp3')
]

VIEWS = [
    models.Ref.directory(
        name='Title',
        uri='internetarchive:directory?sort=title%20asc'
    ),
    models.Ref.directory(
        name='Creator',
        uri='internetarchive:directory?sort=creator%20asc')
]


def test_has_root_directory(library):
    assert library.root_directory == models.Ref.directory(
        name='Internet Archive', uri='internetarchive:'
    )


def test_browse_root_directory(library, client_mock, root_collections):
    results = library.browse(library.root_directory.uri)
    assert client_mock.search.called_once()
    assert results == root_collections


def test_browse_collection(library, client_mock):
    client_mock.getitem.return_value = COLLECTION
    results = library.browse('internetarchive:directory')
    client_mock.getitem.assert_called_once_with('directory')
    assert results == VIEWS


def test_browse_audio(library, client_mock):
    client_mock.getitem.return_value = ITEM
    results = library.browse('internetarchive:album')
    client_mock.getitem.assert_called_once_with('album')
    assert results == TRACKS


def test_browse_video(library, client_mock):
    client_mock.getitem.return_value = {
        'files': [],
        'metadata': {
            'identifier': 'item',
            'mediatype': 'video'
        }
    }
    results = library.browse('internetarchive:album')
    client_mock.getitem.assert_called_once_with('album')
    assert results == []


def test_browse_view(library, client_mock):
    client_mock.search.return_value = client_mock.SearchResult({
        'responseHeader': {
            'params': {
                'q': 'album'
            }
        },
        'response': {
            'docs': [{
                'identifier': 'album',
                'title': 'Album',
                'mediatype': 'audio'
            }, {
                'identifier': 'directory',
                'title': 'Directory',
                'mediatype': 'collection'
            }],
            'numFound': 2
        }
    })
    results = library.browse('internetarchive:audio?sort=title%20asc')
    assert library.backend.client.search.called_once()
    assert results == [
        models.Ref.album(name='Album', uri='internetarchive:album'),
        models.Ref.directory(name='Directory', uri='internetarchive:directory')
    ]


def test_browse_file(library, client_mock):
    results = library.browse('internetarchive:album#file.mp3')
    client_mock.getitem.assert_not_called()
    client_mock.search.assert_not_called()
    assert results == []
