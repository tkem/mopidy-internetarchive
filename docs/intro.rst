Introduction
========================================================================

About the Internet Archive Metadata Model
------------------------------------------------------------------------

.. note::

   This is just a brief introduction to get you accustomed to some
   basic Internet Archive concepts and terminology related to this
   Mopidy extension.  For more in-depth information, please refer to
   the FAQ_ or this `blog post`_.

Files published on the Internet Archive are organized in so-called
*items*.  An item is a directory or folder that includes the
originally uploaded content – audio, video, text, etc. – along with
any derivative files created from the originals, and some metadata
that describes the item.  An item may contain a single audio file, or
a related set of audio files that represent a CD or a taped live
concert.  All the files within an item have the same metadata, such as
(album) title, creator, description, and so on.  For the purpose of
this Mopidy extension, Internet Archive items are treated as *albums*,
and the included audio files show up as the album's *tracks*.

Every item also has a unique identifier, which can be used to access
the item on the Internet Archive's Web site::

  http://archive.org/details/{identifier}

Besides items containing media files, there are also *collections*,
which are used to to group related items.  The `Audio Archive`_, for
example, is the collection item with the identifier *audio*.  An item
can be a member of more than one collection, and collections may also
have sub-collections.  Collections show up as *directories* when
browsing Mopidy.


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
147,929 audio items of the Live Music Archive [#footnote1]_.  The
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


.. _FAQ: https://archive.org/about/faqs.php

.. _blog post: https://blog.archive.org/2011/03/31/how-archive-org-items-are-structured/

.. _Audio Archive: https://archive.org/details/audio

.. _archive.org: https://archive.org/

.. _Virtual Library Card: https://archive.org/account/login.createaccount.php

.. _Archive Favorites: https://archive.org/bookmarks.php

.. rubric:: Footnotes

.. [#footnote1] As of Dec. 7, 2015.
