from __future__ import unicode_literals

from mopidy import models

from mopidy_internetarchive import translator

import pytest


def test_parse_bitrate():
    assert translator.parse_bitrate(None) is None
    assert translator.parse_bitrate('') is None
    assert translator.parse_bitrate([]) is None
    assert translator.parse_bitrate('tmp') is None

    assert translator.parse_bitrate(None, 42) == 42
    assert translator.parse_bitrate('', 42) == 42
    assert translator.parse_bitrate([], 42) == 42
    assert translator.parse_bitrate('tmp', 42) == 42

    assert translator.parse_bitrate('0') == 0
    assert translator.parse_bitrate('1') == 1000
    assert translator.parse_bitrate('42.123') == 42123


def test_parse_date():
    assert translator.parse_date(None) is None
    assert translator.parse_date('') is None
    assert translator.parse_date([]) is None
    assert translator.parse_date('tmp') is None

    assert translator.parse_date(None, 42) == 42
    assert translator.parse_date('', 42) == 42
    assert translator.parse_date([], 42) == 42
    assert translator.parse_date('tmp', 42) == 42

    assert translator.parse_date('2014-02-21T06:00:00Z') == '2014-02-21'
    assert translator.parse_date('2014-02-21') == '2014-02-21'
    assert translator.parse_date('2014-02') == '2014-02-01'
    assert translator.parse_date('2014') == '2014-01-01'


def test_parse_length():
    assert translator.parse_length(None) is None
    assert translator.parse_length('') is None
    assert translator.parse_length([]) is None
    assert translator.parse_length('tmp') is None

    assert translator.parse_length(None, 42) == 42
    assert translator.parse_length('', 42) == 42
    assert translator.parse_length([], 42) == 42
    assert translator.parse_length('tmp', 42) == 42

    assert translator.parse_length('0') == 0
    assert translator.parse_length('1') == 1 * 1000
    assert translator.parse_length('60') == 60 * 1000
    assert translator.parse_length('1:00') == 60 * 1000
    assert translator.parse_length('60:00') == 3600 * 1000
    assert translator.parse_length('1:00:00') == 3600 * 1000


def test_parse_mtime():
    assert translator.parse_mtime(None) is None
    assert translator.parse_mtime('') is None
    assert translator.parse_mtime([]) is None
    assert translator.parse_mtime('tmp') is None

    assert translator.parse_mtime(None, 42) == 42
    assert translator.parse_mtime('', 42) == 42
    assert translator.parse_mtime([], 42) == 42
    assert translator.parse_mtime('tmp', 42) == 42

    assert translator.parse_mtime('0') == 0
    assert translator.parse_mtime('1') == 1


def test_parse_track():
    assert translator.parse_track(None) is None
    assert translator.parse_track('') is None
    assert translator.parse_track([]) is None
    assert translator.parse_track('tmp') is None

    assert translator.parse_track(None, 42) == 42
    assert translator.parse_track('', 42) == 42
    assert translator.parse_track([], 42) == 42
    assert translator.parse_track('tmp', 42) == 42

    assert translator.parse_track('0') == 0
    assert translator.parse_track('1') == 1
    assert translator.parse_track('1/100') == 1
    assert translator.parse_track('1/tmp') == 1


def test_uri(uri=translator.uri):
    assert 'internetarchive:' == uri()
    assert 'internetarchive:item' == uri('item')
    assert 'internetarchive:item#file.mp3' == uri('item', 'file.mp3')
    assert 'internetarchive:item#file%201.mp3' == uri('item', 'file 1.mp3')
    assert 'internetarchive:?q=foo' == uri(q='foo')
    assert 'internetarchive:?q=foo%20AND%20bar' == uri(
        q='foo AND bar'
    )
    assert 'internetarchive:item?sort=title%20asc' == uri(
        'item', sort='title asc'
    )


def test_ref(ref=translator.ref):
    assert models.Ref.album(name='foo', uri='internetarchive:foo') == ref({
        'identifier': 'foo',
        'mediatype': 'audio'
    })
    assert models.Ref.directory(name='foo', uri='internetarchive:foo') == ref({
        'identifier': 'foo',
        'mediatype': 'collection'
    })
    assert models.Ref.directory(name='foo', uri='internetarchive:foo') == ref({
        'identifier': 'foo',
        'mediatype': 'collection'
    })
    assert models.Ref.album(name='Foo', uri='internetarchive:foo') == ref({
        'identifier': 'foo',
        'mediatype': 'audio',
        'title': 'Foo'
    })
    assert models.Ref.directory(name='Foo', uri='internetarchive:foo') == ref({
        'identifier': 'foo',
        'mediatype': 'collection',
        'title': 'Foo'
    })
    # as of Dec 2016, items in oldtimeradio collections return title as list
    assert models.Ref.album(name='#1', uri='internetarchive:otr') == ref({
        'identifier': 'otr',
        'mediatype': 'audio',
        'title': ['#1', '#2']
    })
    assert models.Ref.directory(name='#1', uri='internetarchive:otr') == ref({
        'identifier': 'otr',
        'mediatype': 'collection',
        'title': ['#1', '#2']
    })


def test_artists(artists=translator.artists):
    assert artists({}) is None
    assert artists({'artist': ''}) is None
    assert artists({'creator': ''}) is None
    assert artists({'artist': '', 'creator': ''}) is None
    assert artists({'creator': []}) is None
    assert artists({'artist': '', 'creator': []}) is None
    assert [models.Artist(name='foo')] == artists({
        'artist': 'foo'
    })
    assert [models.Artist(name='foo')] == artists({
        'creator': 'foo'
    })
    assert [models.Artist(name='foo')] == artists({
        'artist': 'foo', 'creator': 'bar'
    })
    assert [models.Artist(name='foo')] == artists({
        'creator': ['foo']
    })
    assert [models.Artist(name='foo'), models.Artist(name='bar')] == artists({
        'creator': ['foo', 'bar']
    })
    assert [models.Artist(name='foo')] == artists({
        'artist': 'foo', 'creator': ['bar', 'baz']
    })


def test_album(album=translator.album):
    model = models.Album(name='foo', uri='internetarchive:foo')
    assert model == album({
        'identifier': 'foo'
    })
    assert model.replace(name='Foo') == album({
        'identifier': 'foo', 'title': 'Foo'
    })
    assert model.replace(artists=[models.Artist(name='bar')]) == album({
        'identifier': 'foo', 'creator': 'bar'
    })
    assert model.replace(date='1970-01-01') == album({
        'identifier': 'foo', 'date': '1970-01-01'
    })


def test_query(query=translator.query):
    assert r'"foo"' == query({'any': ['foo']})
    assert r'"foo \"bar\""' == query({'any': ['foo "bar"']})
    assert r'"foo" AND "bar"' == query({'any': ['foo', 'bar']})
    assert r'title:("foo")' == query({'album': ['foo']})
    assert r'title:("foo bar")' == query({'album': ['foo bar']})
    assert r'title:("foo" "bar")' == query({'album': ['foo', 'bar']})
    assert r'creator:("foo")' == query({'albumartist': ['foo']})
    assert r'creator:("foo" "bar")' == query({'albumartist': ['foo', 'bar']})
    assert r'creator:("foo")' == query({'artist': ['foo']})
    assert r'creator:("foo" "bar")' == query({'artist': ['foo', 'bar']})
    assert r'date:"1970"' == query({'date': ['1970']})
    assert r'date:"1970-01-01"' == query({'date': ['1970-01-01']})


def test_query_exact(query=translator.query):
    with pytest.raises(ValueError):
        query({'any': ['foo']}, exact=True)


def test_query_unsupported(query=translator.query):
    with pytest.raises(ValueError):
        query({'track_name': ['foo']})


def test_query_uris(query=translator.query):
    assert r'"foo"' == query({'any': ['foo']}, [])
    assert r'"foo"' == query({'any': ['foo']}, [''])
    assert r'"foo"' == query({'any': ['foo']}, ['internetarchive:'])

    assert r'"foo" AND collection:(bar)' == query(
        {'any': ['foo']},
        ['internetarchive:bar']
    )
    assert r'"foo" AND collection:(bar OR baz)' == query(
        {'any': ['foo']},
        ['internetarchive:bar', 'internetarchive:baz']
    )

    with pytest.raises(ValueError):
        query({'any': ['foo']}, ['internetarchive:?foo'])
    with pytest.raises(ValueError):
        query({'any': ['foo']}, ['internetarchive:#foo'])
