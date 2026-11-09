import pytest
import requests
from mopidy import models

from mopidy_internetarchive.client import InternetArchiveClient

ERRORS = [
    LookupError("null"),
    requests.ConnectionError("connection refused"),
    requests.Timeout("timed out"),
    InternetArchiveClient.SearchError("empty response"),
]


@pytest.mark.parametrize("error", ERRORS)
@pytest.mark.parametrize(
    "uri", ["internetarchive:", "internetarchive:item", "internetarchive:item?sort=x"]
)
def test_browse_error(library, client_mock, uri, error):
    client_mock.getitem.side_effect = error
    client_mock.search.side_effect = error
    assert library.browse(uri) == []


@pytest.mark.parametrize("error", ERRORS)
@pytest.mark.parametrize("uri", ["internetarchive:item", "internetarchive:item#file"])
def test_lookup_error(library, client_mock, uri, error):
    client_mock.getitem.side_effect = error
    assert library.lookup(uri) == []


@pytest.mark.parametrize("error", ERRORS)
def test_search_error(library, client_mock, error):
    client_mock.search.side_effect = error
    assert library.search({"any": ["foo"]}) == models.SearchResult()
