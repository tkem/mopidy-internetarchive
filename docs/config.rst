Configuration
========================================================================

Configuration items are still subject to change at this point, so be
warned if trying any of these:

.. confval:: internetarchive/base_url

   Base URL to access the `Internet Archive`_.

.. confval:: internetarchive/collections

   Collections for searching/browsing.

.. confval:: internetarchive/mediatypes

   Media types for searching/browsing.

.. confval:: internetarchive/formats

   Audio file formats, in order of preference.

.. confval:: internetarchive/excludes

   Collections to exclude from searching/browsing.

.. confval:: internetarchive/bookmarks

   User names for bookmark browsing.

.. confval:: internetarchive/sort_order

   Sort order for browsing: ``<fieldname> (asc|desc)``, where
   ``<fieldname>`` is one of:

   - avg_rating
   - creatorSorter
   - date
   - downloads
   - month
   - publicdate
   - stars
   - titleSorter
   - week
   - year

.. confval:: internetarchive/search_limit

   Maximum number of search results.

.. confval:: internetarchive/browse_limit

   Maximum number of browse results.

.. confval:: internetarchive/browse_label

   Top-level directory name for browsing.

.. confval:: internetarchive/bookmarks_label

   Bookmark directory names for browsing; {0} is user name

.. confval:: internetarchive/cache_size

   Number of items and query results to cache.

.. confval:: internetarchive/cache_ttl

   Cache time-to-live in seconds.

.. confval:: internetarchive/timeout

   Optional http request timeout in seconds.


Default Configuration
------------------------------------------------------------------------

.. literalinclude:: ../mopidy_internetarchive/ext.conf
   :language: ini

.. _Internet Archive: http://archive.org
