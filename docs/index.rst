Mopidy-InternetArchive
========================================================================

Mopidy-InternetArchive is a Mopidy_ extension for playing music from
the `Internet Archive`_.

This extension lets you search for and stream recordings ranging from
`alternative news programming`_, to `Grateful Dead concerts`_, to `Old
Time Radio shows`_, to `book and poetry readings`_, to `original
music`_ uploaded by Internet Archive users.  It also gives you access
to a vast number of high-quality live recordings from the `Live Music
Archive`_, and thousands of free audiobooks from the LibriVox_
collection.


Browsing the Internet Archive
------------------------------------------------------------------------

If your Mopidy client supports browsing, there should be a top-level
directory named *Internet Archive*.  Beneath that, you will find the
Internet Archive collections listed in
:confval:`internetarchive/collections`, and you should be able to
browse individual audio items (albums) and files (tracks) within
these.

For practical and performance reasons, the number of items that will
be shown within a collection is limited, e.g. you will not see all
167,967 audio items of the Live Music Archive [#footnote1]_.  The
:ref:`default configuration <defconf>` sets this limit to 100, but
this can be changed using :confval:`internetarchive/browse_limit`.

To allow browsing collections using different sort criteria, every
collection provides a number of *views*, virtual subdirectories which
let you browse the collection's items by popularity, title, publish
date, and so on.  The default views are set up to resemble the
archive.org_ Web interface, but can be changed at your own discretion
with :confval:`internetarchive/browse_views`.


Searching the Internet Archive
------------------------------------------------------------------------

The Internet Archive only supports searching for *items*, but not for
individual files or tracks.  Therefore, only *albums* will show up
when searching in Mopidy.  This also means that only album-related
search fields are supported, so searching for track names or numbers
will yield no results from the Internet Archive.

The number and ordering of search results returned from the Internet
Archive can be changed with :confval:`internetarchive/search_limit`
and :confval:`internetarchive/search_order`.  Unless you explicitly
specify an Internet Archive collection to search within, search scope
will also be limited to the collections listed in
:confval:`internetarchive/collections`.


Archive Favorites
------------------------------------------------------------------------

If you have an Internet Archive account - also termed a `Virtual
Library Card`_ - you can access your `Archive Favorites`_ from Mopidy.
To do so, you just need to add the identifier of your favorites
collection to :confval:`internetarchive/collections`.  Typically, the
identifier is *fav-{username}*, but you should be able to figure it
out from the archive.org_ Web site.  When added to
:confval:`internetarchive/collections`, you will be able to browse and
search your Archive Favorites just like the other collections listed
there.


.. toctree::
   :hidden:

   install
   config
   changelog
   license


.. rubric:: Footnotes

.. [#footnote1] As of Jan. 9, 2017.


.. _Mopidy: http://www.mopidy.com/
.. _Internet Archive: http://archive.org
.. _alternative news programming: https://archive.org/details/audio_news
.. _Grateful Dead concerts: https://archive.org/details/GratefulDead
.. _Old Time Radio shows: https://archive.org/details/radioprograms
.. _book and poetry readings: https://archive.org/details/audio_bookspoetry
.. _original music: https://archive.org/details/opensource_audio
.. _Live Music Archive: https://archive.org/details/etree
.. _LibriVox: https://archive.org/details/librivoxaudio

.. _archive.org: https://archive.org/
.. _Virtual Library Card: https://archive.org/account/login.createaccount.php
.. _Archive Favorites: https://archive.org/bookmarks.php
