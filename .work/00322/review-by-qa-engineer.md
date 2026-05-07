# Expert Review: QA Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files

## Summary

0 Findings (all Findings from the initial review have been resolved)

## Findings

All Findings from the initial review were resolved:

**QA-F1 (Resolved)** — xlsx single-sheet branch (`len(sheet_names) == 1`) had no
test coverage.

- **Fix applied**: Added `test_classify_sources_single_sheet_xlsx_no_sheet_suffix`
  (asserts `file_id == "test-spec"`, no `-Only` suffix) and
  `test_classify_sources_multi_sheet_xlsx_gets_sheet_suffix` (asserts 2 entries
  with `-A`/`-B` suffixes). Both use `monkeypatch` to stub `derive_file_id` and
  `_load_mappings`, avoiding filesystem dependencies.

**QA-F2 (Resolved)** — `classify_sources([])` empty-input path had no test coverage.

- **Fix applied**: Added `test_classify_sources_empty_input` with `_load_mappings`
  stubbed; asserts `result == []`.

**QA-F3 (Resolved)** — v1.x path (`iterdir()` + all-releasenote) was not exercised
by any test.

- **Fix applied**: Added `test_scan_sources_v1x_iterdir_path` which builds a minimal
  v1.4-style tree under `tmp_path` and calls `scan_sources("1.4", tmp_path, files=[...])`
  to confirm the `files=` path works for v1.x versions.

**QA-F4 (Resolved)** — `scan_sources` with absolute path input had no success-path test.

- **Fix applied**: Added `test_scan_sources_absolute_path_input` which passes
  `str(rst_file)` (absolute) to `scan_sources(..., files=[...])` and asserts the
  returned `SourceFile` has the correct `path` and `format`.

## Observations

- `test_scan_sources_v1x_iterdir_path` exercises the `files=` branch only. A full
  directory-scan test for v1.x would require `.lw/nab-official/v1.4/` to be present
  in the test environment; that is an integration concern and out of scope for unit tests.

## Positive Aspects

- All new tests use `monkeypatch` to avoid real filesystem mapping dependencies,
  keeping them fast and hermetic.
- 488 tests pass (up from 483 before this PR).
- Test names are descriptive and map 1:1 to the edge cases they cover.

## Files Reviewed

- `tests/ut/test_sources.py` (tests)
- `scripts/common/sources.py` (source code — implementation being tested)
