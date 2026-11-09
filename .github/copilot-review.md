# Code Review — Mopidy-InternetArchive 4.0.1

**Date:** 2026-11-09
**Reviewed:** `develop` at `4fe3a0b` ("Fix tests failing when a single test file is
run."), i.e. v4.0.1 plus the build environment update and the fixes for client
errors in the library provider.

**CI status:** All default `tox` environments pass locally on CPython 3.13.18 (`py`:
70 passed) with Mopidy 4.0.5, requests 2.34.2, cachetools 8.0.0 and uritools 7.0.0;
not run on 3.14 locally. GitHub Actions passed on 3.13 and 3.14 for the merged PRs;
its run for this commit had not finished when this review was written. `tox -e
pyright` fails with 75 errors (Code #2). **Coverage:** 82 % with branches;
`library.py`, `translator.py` and `playback.py` are at 95–100 %, but `backend.py`
(37 %) and `client.py` (38 %) are never exercised, since all provider tests use a
mock client.

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `playback.py` `translate_uri` | Album and collection URIs without a filename translate to `/download/<identifier>`, an HTML directory listing, instead of `None`. |
| 2 | Low | whole package, `tests/` | pyright `standard` reports 75 errors: Mopidy 4's typed models (`Uri`, `ReleaseDate`, `DurationMs`, `tuple` search results, hashable `Artist`) reject plain values, `self.backend.client` is unknown on `backend.Backend`, `re.match()` results are not checked for `None`, and `conftest.py` reaches the submodules through the `ext` alias, which pyright does not resolve. Blocks adding `pyright` to the envlist. |

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | `InternetArchiveClient` and `InternetArchiveBackend` have no tests: caching, `SearchError` for empty responses, `LookupError` for `error` results, proxy and user agent setup are unverified. |
| 2 | Low | The `get_images()` error path (lines 66–67) is untested; `tests/test_errors.py` covers only `browse()`, `lookup()` and `search()`. |
| 3 | Info | Two `DeprecationWarning`s come from `mopidy.types` at import time, not from this package. |

## Changelog

| # | Priority | Finding |
|---|----------|---------|
| 1 | Medium | The next release's entry needs a line for the changed behavior, e.g. "Log errors and return empty results from ``browse()``, ``lookup()`` and ``search()`` instead of raising.", plus "Update build environment." for the ruff, `tox` and CI changes and one "Minor test improvements." line. |
