from __future__ import unicode_literals

from mopidy import models


def test_search_any(library, client_mock):
    client_mock.search.return_value = client_mock.SearchResult({
        'responseHeader': {
            'params': {
                'query': 'album'
            }
        },
        'response': {
            'docs': [{
                'identifier': 'album1',
                'title': 'Album #1',
                'mediatype': 'audio'
            }, {
                'identifier': 'album2',
                'title': 'Album #2',
                'mediatype': 'etree'
            }],
            'numFound': 2
        }
    })
    result = library.search(dict(any=['album']))
    assert client_mock.search.called_once()
    assert result == models.SearchResult(
        uri='internetarchive:?q=album',
        albums=[
            models.Album(name='Album #1', uri='internetarchive:album1'),
            models.Album(name='Album #2', uri='internetarchive:album2')
        ]
    )


def test_search_unknown(library, client_mock):
    result = library.search(dict(foo=['bar']))
    client_mock.search.assert_not_called()
    assert result is None
