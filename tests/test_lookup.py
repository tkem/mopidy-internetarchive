from __future__ import unicode_literals

from mopidy import models

import pytest

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

ALBUM = models.Album(
    name='Album',
    uri='internetarchive:album'
)

TRACK1 = models.Track(
    album=ALBUM,
    name='Track #1',
    track_no=1,
    uri='internetarchive:album#track01.mp3'
)

TRACK2 = models.Track(
    album=ALBUM,
    name='Track #2',
    track_no=2,
    uri='internetarchive:album#track02.mp3'
)


def test_lookup_root(library, client_mock):
    assert library.lookup('internetarchive:') == []


def test_lookup_album(library, client_mock):
    client_mock.getitem.return_value = ITEM
    results = library.lookup('internetarchive:album')
    client_mock.getitem.assert_called_once_with('album')
    assert results == [TRACK1, TRACK2]


def test_lookup_track(library, client_mock):
    client_mock.getitem.return_value = ITEM
    results = library.lookup('internetarchive:album#track01.mp3')
    client_mock.getitem.assert_called_once_with('album')
    assert results == [TRACK1]
    # assert lookup cache is used
    client_mock.reset_mock()
    results = library.lookup('internetarchive:album#track02.mp3')
    client_mock.getitem.assert_not_called()
    assert results == [TRACK2]


def test_lookup_refresh(library, client_mock):
    client_mock.getitem.return_value = ITEM
    results = library.lookup('internetarchive:album#track01.mp3')
    client_mock.getitem.assert_called_once_with('album')
    assert results == [TRACK1]
    # clear lookup cache
    library.refresh()
    assert client_mock.cache.clear.called
    # assert lookup cache is cleared
    client_mock.reset_mock()
    results = library.lookup('internetarchive:album#track02.mp3')
    client_mock.getitem.assert_called_once_with('album')
    assert results == [TRACK2]


def test_lookup_unknown(library, client_mock):
    client_mock.getitem.side_effect = LookupError('null')
    with pytest.raises(LookupError):
        library.lookup('internetarchive:null')
    client_mock.getitem.assert_called_once_with('null')
