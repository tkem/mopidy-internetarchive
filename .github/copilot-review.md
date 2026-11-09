# Code Review — Mopidy-InternetArchive 4.0.1

**Date:** 2026-11-09
**Reviewed:** branch `build-environment` (two commits: "Update build environment and
add AGENTS.md." and "Configure ruff and pyright, apply ruff fixes."), based on
`develop` at `85079e1` ("Bump actions/checkout from 6.0.2 to 7.0.0"), i.e. v4.0.1
plus dependency bumps.

**CI status:** All default `tox` environments pass locally on CPython 3.13.18 (`py`:
46 passed) with Mopidy 4.0.5, requests 2.34.2, cachetools 8.0.0 and uritools 7.0.0;
not run on 3.14. `tox -e pyright` fails with 75 errors (Code #5). GitHub Actions has
not run for this branch. **Coverage:** 81 % with branches; `library.py`,
`translator.py` and `playback.py` are at 95–100 %, but `backend.py` (37 %) and
`client.py` (38 %) are never exercised, since all provider tests use a mock client.

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Medium | `library.py` `browse`, `lookup`, `search` | Client errors are not caught: an unknown identifier (`LookupError` from `getitem()`), `requests.ConnectionError`/timeouts and `SearchError` propagate to Mopidy; only `get_images()` logs and skips. Probed with the client's methods patched to raise. |
| 2 | Low | `library.py` `lookup` | A track URI whose filename is not among the item's tracks in the configured `audio_formats` (e.g. after changing them) raises `KeyError` from `trackmap[uri]` instead of returning `[]`. |
| 3 | Low | `library.py` `browse` | Query parameters are passed as keyword arguments to `__browse_collection()`, so any key but `sort` (e.g. `internetarchive:audio?foo=bar`) raises `TypeError`. |
| 4 | Low | `playback.py` `translate_uri` | Album and collection URIs without a filename translate to `/download/<identifier>`, an HTML directory listing, instead of `None`. |
| 5 | Low | whole package, `tests/` | pyright `standard` reports 75 errors: Mopidy 4's typed models (`Uri`, `ReleaseDate`, `DurationMs`, `tuple` search results, hashable `Artist`) reject plain values, `self.backend.client` is unknown on `backend.Backend`, `re.match()` results are not checked for `None`, and `conftest.py` uses `ext.client` etc. without importing them. Blocks adding `pyright` to the envlist. |

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | `InternetArchiveClient` and `InternetArchiveBackend` have no tests: caching, `SearchError` for empty responses, `LookupError` for `error` results, proxy and user agent setup are unverified. |
| 2 | Low | No test covers client errors in `browse()`, `lookup()` or `search()` (Code #1–#3), nor the `get_images()` error path (lines 62–63). |
| 3 | Info | Two `DeprecationWarning`s come from `mopidy.types` at import time, not from this package. |

## Docs (`docs/index.rst`)

| # | Priority | Finding |
|---|----------|---------|
| 1 | Info | `README.rst` still shows a "code style: black" badge, although formatting is done with `ruff format`. |

## Changelog

| # | Priority | Finding |
|---|----------|---------|
| 1 | Info | The build changes on this branch (ruff configuration, `tox` and CI updates) need an "Update build environment." line in the next release's entry. |
