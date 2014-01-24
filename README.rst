****************************
Mopidy-InternetArchive
****************************

.. image:: https://pypip.in/v/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/tkem/mopidy-internetarchive.png?branch=master
    :target: https://travis-ci.org/tkem/mopidy-internetarchive
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/tkem/mopidy-internetarchive/badge.png?branch=master
   :target: https://coveralls.io/r/tkem/mopidy-internetarchive?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for playing music and
audio from the `Internet Archive <http://archive.org>_.`


Installation
============

Install by running::

    pip install Mopidy-InternetArchive

Or install Debian/Ubuntu packages for `Mopidy-InternetArchive releases
<https://github.com/tkem/mopidy-internetarchive/releases>`_.


Configuration
=============

Configuration items are very much subject to change at this point, so
be warned before trying any of these::

    [internetarchive]

    # archive.org base URL; change to https if you like
    base_url = http://archive.org

    # limit search to specific collections, e.g. etree
    collection =

    # limit search to specific mediatypes, e.g. etree
    mediatype = audio, etree

    # streaming formats in order of preference
    format = VBR MP3, MP3, Ogg Vorbis, Flac

    # limit number of search results if set
    limit =


Project resources
=================

- `Source code <https://github.com/tkem/mopidy-internetarchive>`_
- `Issue tracker <https://github.com/tkem/mopidy-internetarchive/issues>`_
- `Download development snapshot <https://github.com/tkem/mopidy-internetarchive/tarball/master#egg=Mopidy-InternetArchive-dev>`_


Changelog
=========

v0.1.0 (2014-01-24)
----------------------------------------

- Initial release.
