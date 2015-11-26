from __future__ import unicode_literals

from mopidy import models

URL = 'http://archive.org/download/album/cover.jpg'

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
    }, {
        'name': 'cover.jpg',
        'format': 'JPEG'
    }],
    'metadata': {
        'identifier': 'album',
        'title': 'Album',
        'mediatype': 'audio'
    }
}

IMAGES = [
    models.Image(uri=URL)
]


def test_root_images(library, client_mock):
    results = library.get_images(['internetarchive:'])
    client_mock.getitem.assert_not_called()
    assert results == {}


def test_album_images(library, client_mock):
    client_mock.getitem.return_value = ITEM
    client_mock.geturl.return_value = URL
    results = library.get_images(['internetarchive:album'])
    client_mock.getitem.assert_called_once_with('album')
    assert results == {'internetarchive:album': IMAGES}


def test_track_images(library, client_mock):
    client_mock.getitem.return_value = ITEM
    client_mock.geturl.return_value = URL
    results = library.get_images([
        'internetarchive:album#track01.jpg',
        'internetarchive:album#track02.jpg',
    ])
    client_mock.getitem.assert_called_once_with('album')
    assert results == {
        'internetarchive:album#track01.jpg': IMAGES,
        'internetarchive:album#track02.jpg': IMAGES
    }
