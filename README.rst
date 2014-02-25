************************************************************************
Mopidy-InternetArchive
************************************************************************

Mopidy_ extension for playing music and audio from the `Internet
Archive <http://archive.org>`_.


Installation
========================================================================

Install by running::

    pip install Mopidy-InternetArchive

You can also download and install Debian/Ubuntu packages for
Mopidy-InternetArchive `releases
<https://github.com/tkem/mopidy-internetarchive/releases>`_.


Configuration
========================================================================

Configuration items are still subject to change at this point, so be
warned if trying any of these::

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

    # audio file formats, in order of preference
    formats = VBR MP3, MP3

    # collections to exclude from searching/browsing
    excludes =

    # user names for bookmark browsing
    bookmarks =

    # sort order for browsing: <fieldname> (asc|desc), where <fieldname>
    # is one of: avg_rating, creatorSorter, date, downloads, month,
    # publicdate, stars, titleSorter, week, year
    sort_order = downloads desc

    # maximum number of search results
    search_limit = 100

    # maximum number of browse results
    browse_limit = 100

    # top-level directory name for browsing
    browse_label = Internet Archive

    # bookmark directory names for browsing; {0} is user name
    bookmarks_label = {0}'s Bookmarks

    # number of items and query results to cache
    cache_size = 128

    # cache time-to-live in seconds
    cache_ttl = 86400

    # optional http request timeout in seconds
    timeout =


Project resources
========================================================================

.. TODO - `Documentation <http://mopidy-internetarchive.readthedocs.org/en/docs/>`_
- `Issue Tracker <https://github.com/tkem/mopidy-internetarchive/issues>`_
- `Source Code <https://github.com/tkem/mopidy-internetarchive>`_
- `Change Log <https://github.com/tkem/mopidy-internetarchive/CHANGELOG.rst>`_


.. image:: https://pypip.in/v/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-InternetArchive/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-InternetArchive/
    :alt: Number of PyPI downloads

.. _Mopidy: http://www.mopidy.com/
