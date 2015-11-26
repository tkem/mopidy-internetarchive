from __future__ import unicode_literals

import collections
import re

from mopidy.config import types

from mopidy_internetarchive import ConfigMap

import pytest


def test_deserialize():
    expected = collections.OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])
    type = ConfigMap()
    assert type.deserialize(b'a|1, b|2 , c|3') == expected
    assert type.deserialize(b'a|1\n b|2 \nc|3') == expected

    with pytest.raises(ValueError):
        type.deserialize(b'')
    with pytest.raises(ValueError):
        type.deserialize(b'a')
    with pytest.raises(ValueError):
        type.deserialize(b'a|')
    with pytest.raises(ValueError):
        type.deserialize(b'|1')


def test_deserialize_choice_keys():
    expected = collections.OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])
    type = ConfigMap(keys=types.String(choices=['a', 'b', 'c']))
    assert type.deserialize(b'a|1, b|2 , c|3') == expected
    assert type.deserialize(b'a|1\n b|2 \nc|3') == expected

    with pytest.raises(ValueError):
        type.deserialize(b'x|0')


def test_deserialize_integer_keys():
    expected = collections.OrderedDict([(1, 'a'), (2, 'b'), (3, 'c')])
    type = ConfigMap(keys=types.Integer())
    assert type.deserialize(b'1|a, 2|b , 3|c') == expected
    assert type.deserialize(b'1|a\n 2|b \n3|c') == expected


def test_deserialize_list_keys():
    expected = collections.OrderedDict([(('a', ), '1'), (('b', 'c'), '2')])
    type = ConfigMap(keys=types.List())
    assert type.deserialize(b'a|1\n b, c|2') == expected


def test_deserialize_choice_values():
    expected = collections.OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])
    type = ConfigMap(values=types.String(choices=['1', '2', '3']))
    assert type.deserialize(b'a|1, b|2 , c|3') == expected
    assert type.deserialize(b'a|1\n b|2 \nc|3') == expected

    with pytest.raises(ValueError):
        type.deserialize(b'x|0')


def test_deserialize_integer_values():
    expected = collections.OrderedDict([('a', 1), ('b', 2), ('c', 3)])
    type = ConfigMap(values=types.Integer())
    assert type.deserialize(b'a|1, b|2 , c|3') == expected
    assert type.deserialize(b'a|1\n b|2 \nc|3') == expected

    with pytest.raises(ValueError):
        type.deserialize(b'x|y')


def test_deserialize_list_values():
    expected = collections.OrderedDict([('a', ('1', )), ('b', ('2', '3'))])
    type = ConfigMap(values=types.List())
    assert type.deserialize(b'a|1\n b|2,3') == expected


def test_deserialize_optional_values():
    expected = collections.OrderedDict([('a', '1'), ('b', None), ('c', None)])
    type = ConfigMap(values=types.String(optional=True))
    assert type.deserialize(b'a|1, b| , c') == expected
    assert type.deserialize(b'a|1\n b| \nc') == expected


def test_delim():
    expected = collections.OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])
    type = ConfigMap(delim=':')
    assert type.deserialize(b'a:1, b: 2 , c :3') == expected
    assert type.deserialize(b'a:1\n b: 2 \nc :3') == expected


def test_optional():
    expected = collections.OrderedDict()
    assert ConfigMap(optional=True).deserialize(b'') == expected

    with pytest.raises(ValueError):
        ConfigMap(optional=False).deserialize(b'')
    with pytest.raises(ValueError):
        ConfigMap().deserialize(b'')


def test_serialize():
    type = ConfigMap(keys=types.String(), values=types.Integer())
    value = collections.OrderedDict([('a', 1), ('b', 2), ('c', 3)])
    result = type.serialize(value)
    assert isinstance(result, bytes)
    assert re.match(r'\s*a|1\n\s*b|2\n\s*c|3', result)


def test_serialize_none():
    type = ConfigMap(keys=types.String(), values=types.Integer())
    result = type.serialize(None)
    assert isinstance(result, bytes)
    assert result == b''
