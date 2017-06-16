v2.0.3 (2017-06-16)
-------------------

- Handle archive.org JSON API changes.


v2.0.2 (2017-01-09)
-------------------

- Fix file name handling.


v2.0.1 (2017-01-09)
-------------------

- Handle multiple item titles.


v2.0.0 (2015-12-08)
-------------------

- Support configurable sort criteria when browsing collections via
  "browse views".

- Include collections in browse results.

- Add support for ``LibraryProvider.get_images()``.

- Drop support for deprecated ``Album.images``.

- Drop special handling of bookmarks.

- Cache root collections.

- Update documentation.


v1.3.0 (2015-09-11)
-------------------

- Require Mopidy >= 1.1.

- Use Mopidy proxy settings and HTTP User-Agent.

- Fix track bitrates represented in Kbit/s.

- Drop exact search support.

- Only cache items.


v1.2.1 (2015-03-25)
-------------------

- Remove search query normalization.

- Prepare for Mopidy v1.0 exact search API.


v1.2.0 (2015-03-19)
-------------------

- Remove playlists provider.

- Add bookmarks to root directory for browsing.


v1.1.0 (2014-11-19)
-------------------

- Load bookmarks as individual playlists.

- Clear library cache when refreshing playlists.

- Encode filenames in URIs.

- Add HTTP connection retries.


v1.0.3 (2014-11-14)
-------------------

- Fix handling of re-derived VBR MP3 files.

- Remove Ogg Vorbis from default audio formats.


v1.0.2 (2014-11-07)
-------------------

- Update dependencies.

- Browse Internet Archive items as albums.

- Make caching optional.

- Disable PNG image format in default configuration.

- Temporarily disable VBR MP3 and track comments.


v1.0.1 (2014-09-29)
-------------------

- Add item descriptions as track comments.

- Filter search results for exact queries.


v1.0.0 (2014-09-26)
-------------------

- Major rewrite for version 1.0.0.


v0.5.0 (2014-02-28)
-------------------

- Update `README` with link to documentation.

- New config values: ``search_order``, ``browse_order``.

- Allow empty queries for searching.


v0.4.0 (2014-02-25)
-------------------

- Various performance and stability improvements.

- Option to exclude specific collections from searching/browsing.

- Add image URLs to albums.


v0.3.1 (2014-02-21)
-------------------

- Fix default configuration.


v0.3.0 (2014-02-21)
-------------------

- Add bookmark browsing support.

- Better filtering of search results.

- Stability and performance improvements.


v0.2.0 (2014-01-31)
-------------------

- Add library browsing support.

- Cache search results and metadata.

- Properly quote/encode query terms.


v0.1.0 (2014-01-24)
-------------------

- Initial release.
