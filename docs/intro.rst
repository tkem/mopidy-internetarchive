Introduction
========================================================================

About the Internet Archive Metadata Model
------------------------------------------------------------------------

.. note::

   This is just a brief introduction to get you accustomed to some
   basic Internet Archive concepts and terminology related to this
   Mopidy extension.  For more in-depth information, please refer to
   the FAQ_, or start with this `blog post`_.

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

In Mopidy, you may encounter item identifiers in an album URI's path,
while individual tracks add the respective file name as their URI's
fragment.

Besides items containing media files, there are also *collections*,
which are used to to group related items.  The `Live Music Archive`_,
for example, is the collection with the identifier *etree*.  An item
can be a member of more than one collection, and collections may also
have sub-collections.  Within the Live Music Archive, there exist
sub-collections for all artists that gave permission for live show
recordings to be hosted on archive.org, such as the `Grateful Dead`_
or the `Smashing Pumpkins`_, while the Live Music Archive itself is a
sub-collection of the larger `Audio Archive`_.  Within Mopidy,
collections most prominently show up as top-level directories when
browsing the Internet Archive, but can also be used to :ref:`exclude
<exclude>` specific items from searching and browsing [#footnote1]_.


Browsing the Internet Archive
------------------------------------------------------------------------

Starting with version 0.18, Mopidy also provides the possiblity to
browse directories and tracks.  If your client supports this, there
should be a virtual directory named *Internet Archive*.  When
browsing, Internet Archive items are structured into a hierarchy three
levels deep.  At the top level, you will find the collections
configured under :confval:`internetarchive/collections`, and you will
be able to browse individual audio items (albums) and files (tracks)
within these.

For practical and performance reasons, the number of audio items that
will be shown within a collection is limited, e.g. you will not see
all 132,887 items of the Live Music Archive [#footnote2]_.  The
:ref:`default configuration <defconf>` sets this limit to 100, but
this can be changed with :confval:`internetarchive/browse_limit`.
Items are selected based on popularity by default, i.e. the 100 most
downloaded items will be listed for each collection.  This can also be
changed using :confval:`internetarchive/browse_order`, e.g. to always
show the latest additions to the Archive.


Searching the Internet Archive
------------------------------------------------------------------------

The Internet Archive only supports searching for items, but not for
individual files or tracks.  Therefore, only *albums* will show up
when searching in Mopidy, which may not be handled correctly by your
client.  This also means that only album-related search fields are
supported, i.e. searching for track names or numbers will yield no
results from the Internet Archive.

The number and ordering of search results returned from the Internet
Archive can be changed with :confval:`internetarchive/search_limit`
and :confval:`internetarchive/search_order`, similar to the settings
used for browsing.


Archive Bookmarks
------------------------------------------------------------------------

If you have an Internet Archive account - also termed a `Virtual
Library Card`_ - you can access your `Archive Bookmarks`_ from Mopidy.
To do so, you need to add your Internet Archive user name to Mopidy's
configuration as :confval:`internetarchive/username`.  Your bookmarks
will then appear in the top-level browse directory as *Archive
Bookmarks*.

.. note::

   It is currently not possible to edit your Archive Bookmarks using
   Mopidy.  This restriction may be removed in future versions.


.. _FAQ: https://archive.org/about/faqs.php

.. _blog post: http://blog.archive.org/2011/03/31/how-archive-org-items-are-structured/

.. _Live Music Archive: http://archive.org/details/etree

.. _etree: http://archive.org/details/etree

.. _Grateful Dead: http://archive.org/details/GratefulDead

.. _Smashing Pumpkins: http://archive.org/details/SmashingPumpkins

.. _Audio Archive: https://archive.org/details/audio

.. _Virtual Library Card: https://archive.org/account/login.createaccount.php

.. _Archive Bookmarks: http://archive.org/bookmarks.php

.. rubric:: Footnotes

.. [#footnote1] If you *really* don't like the Grateful Dead, for example.

.. [#footnote2] As of 2014-09-26.
