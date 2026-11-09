# Mopidy-InternetArchive

Mopidy backend extension for browsing, searching and playing audio from the Internet
Archive (archive.org). Pure Python ≥ 3.13, `src/` layout, no annotations; depends on
Mopidy ≥ 4, Pykka, `cachetools`, `requests` and `uritools`. Single maintainer;
`master` is the release branch and `develop` the integration branch that PRs and
Dependabot target. Code reviews follow `.github/copilot-instructions.md`.

## Commands

Run everything through `tox`, never bare `pytest`, `ruff` or `pyright`:

```bash
tox -p auto                                  # default environments, as CI does
tox -e py -- tests/test_browse.py -k root    # tests; posargs go to pytest
tox -e ruff,ruff-format,docs                 # lint, format, docs
tox -e pyright                               # not in envlist yet: still fails
```

Installing Mopidy builds PyGObject, which needs the GObject introspection and cairo
headers (`libgirepository-2.0-dev`, `libcairo2-dev`, `pkg-config` on Debian/Ubuntu).
CI (GitHub Actions on `tkem/mopidy-internetarchive`, every push) runs CPython 3.13
and 3.14 inside the `ghcr.io/mopidy/ci` container; without `gh`, check runs via
`https://api.github.com/repos/tkem/mopidy-internetarchive/actions/runs?branch=<branch>`.
Coverage is reported to Codecov and is not complete; see `.github/copilot-review.md`.
`python -m mopidy_internetarchive.client` queries the live API for manual checks.

## Code Style

- `ruff check` and `ruff format` with the default rules; `[tool.ruff.lint]` in
  `pyproject.toml` ignores `BLE001` (errors are logged and replaced by empty or
  default results on purpose), `RUF012` (Mopidy's class attributes) and `UP031`.
  Do not add `noqa`.
- No type annotations in `src/`; keep the code compatible with pyright's
  `standard` mode where it is cheap to do so.
- Private state uses double-underscore names (`self.__lookup`); all HTTP goes
  through `InternetArchiveClient`, which returns decoded JSON or a `SearchResult`.
- Log with `logger.error("... %s", arg)`, never f-strings, and never raise from
  `browse()`, `lookup()`, `get_images()` or `search()`: Mopidy clients expect an
  empty result. The `translator.parse_*` helpers log and return their default.
- Docs (`docs/index.rst`): wrap prose at column 70, two spaces after a sentence,
  `confval` entries for every setting in `ext.conf`. Keep `README.rst` in sync.

## Architecture Constraints

- URIs are `internetarchive:` (root), `internetarchive:<identifier>` for items and
  collections, `internetarchive:<identifier>#<filename>` for tracks and
  `internetarchive:<identifier>?sort=<field> <order>` for collection views, built by
  `translator.uri()` and split by `translator.parse_uri()`. Saved playlists depend
  on them; keep the encoding stable.
- The client caches `getitem()` in `client.cache` (`LRUCache` or `TTLCache` from
  `cache_size`/`cache_ttl`, or none); `refresh()` clears it together with the
  library's root directories and lookup cache.
- `lookup()` and browsing an item keep the tracks of the last item, so adding a whole
  album to the tracklist does not fetch it once per track.
- Browsing a collection lists its sort views from `browse_views`; searches and
  collection listings are filtered to `audio_formats`, tracks pick the first
  matching format in order of preference, images likewise from `image_formats`.
- `translator.query()` raises `ValueError` for unsupported queries (exact, unknown
  field, non-collection URI); `search()` then returns `None` so Mopidy asks other
  backends. Only the fields in `_QUERYMAP` map to Lucene terms, quoted by `quote()`.
- Configuration keys live in `ext.conf` and `Extension.get_config_schema()`; both
  must change together, as must the test `config` fixture. `ConfigMap` parses
  `browse_views`.

## Testing

- New behavior needs tests under `tests/`; user-visible changes need docs in
  `docs/index.rst`. Tests never touch the network: the library and playback
  providers get a `backend_mock` whose `client_mock` is specced on
  `InternetArchiveClient`, with minimal item and search JSON.
- Translator tests feed raw metadata dicts and compare against Mopidy models.

## Boundaries

- Never edit `CHANGELOG.rst` or bump `__version__`; both are release-only.
- Never change URIs or configuration keys without a deprecation path.
- Do not re-raise the *Maintainer Decisions* in `.github/copilot-instructions.md`.

## Git

- PRs target `develop` and reference an open issue (except trivial fixes), in
  separate commits:
  `Fix #123: ...`, `Tests for #123: ...`, `Docs for #123: ...`.
- Run `tox -p auto` before pushing. Update this file in the same PR that changes a
  convention, and keep it under 100 lines.
