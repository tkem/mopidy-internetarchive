from __future__ import unicode_literals


def test_translate_url(playback, client_mock):
    url = 'http://archive.org/download/item/file.mp3'
    client_mock.geturl.return_value = url
    result = playback.translate_uri('internetarchive:item#file.mp3')
    assert client_mock.geturl.called_once()
    assert client_mock.geturl.call_args == (('item', 'file.mp3'),)
    assert result == url
