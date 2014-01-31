****************************
Mopidy-InternetArchive
****************************

.. image:: https://pypip.in/v/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Number of PyPI downloads

`Mopidy <http://www.mopidy.com/>`_ extension for playing music and
audio from the `Internet Archive <http://archive.org>`_.


Installation
============

Install by running::

    pip install Mopidy-InternetArchive

Or install Debian/Ubuntu packages for `Mopidy-InternetArchive releases
<https://github.com/tkem/mopidy-internetarchive/releases>`_.


Configuration
=============

Configuration items are still subject to change at this point, so be
warned before trying any of these::

  [internetarchive]
  enabled = true

  # archive.org base URL
  base_url = http://archive.org

  # collections for searching/browsing
  collections =
    audio
    audio_bookspoetry
    audio_foreign
    audio_music
    audio_news
    audio_podcast
    audio_religion
    audio_tech
    etree
    netlabels
    opensource_audio
    radioprograms

  # media types for searching/browsing
  mediatypes = audio, etree

  # streaming formats in order of preference
  formats = VBR MP3, MP3

  # query sort order: <fieldname> (asc|desc), ...
  sort_order = downloads desc

  # top-level name for browsing
  browse_label = Internet Archive

  # maximum number of browse results
  browse_limit = 1000

  # maximum number of search results
  search_limit = 100

  # number of items and query results to cache
  cache_size = 128

  # cache time-to-live in seconds
  cache_ttl = 86400


Project resources
=================

- `Source code <https://github.com/tkem/mopidy-internetarchive>`_
- `Issue tracker <https://github.com/tkem/mopidy-internetarchive/issues>`_
- `Download development snapshot <https://github.com/tkem/mopidy-internetarchive/tarball/master#egg=Mopidy-InternetArchive-dev>`_


Changelog
=========

v0.2.0 (2014-01-31)
-------------------

- Add library browsing support.

- Cache search results and metadata.

- Properly quote/encode query terms.

v0.1.0 (2014-01-24)
-------------------

- Initial release.
