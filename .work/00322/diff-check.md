# Diff Check: Issue #322 — Move scan/classify to common

**Date**: 2026-05-07
**Branch**: 322-move-scan-classify-to-common

## Changed Files

| File | Type | Expected? |
|------|------|-----------|
| `tools/rbkc/scripts/common/sources.py` | New | ✅ Yes — new module consolidating SourceFile, FileInfo, scan_sources, classify_sources, _sheet_slug |
| `tools/rbkc/tests/ut/test_sources.py` | New | ✅ Yes — TDD tests for scripts.common.sources |
| `tools/rbkc/scripts/create/scan.py` | Modified | ✅ Yes — replaced with re-export shim |
| `tools/rbkc/scripts/create/classify.py` | Modified | ✅ Yes — replaced with re-export shim |
| `tools/rbkc/scripts/create/differ.py` | Modified | ✅ Yes — import updated to scripts.common.sources |
| `tools/rbkc/scripts/run.py` | Modified | ✅ Yes — imports updated to scripts.common.sources |
| `.work/00322/tasks.md` | Modified | ✅ Yes — task tracking |

## Diff Summary

```
tools/rbkc/scripts/create/classify.py | 218 ++----------------------------
tools/rbkc/scripts/create/differ.py   |   2 +-
tools/rbkc/scripts/create/scan.py     | 120 ++--------------
tools/rbkc/scripts/run.py             |   3 +-
4 modified files: 23 insertions(+), 320 deletions(-)
2 new files: sources.py (~270 lines) + test_sources.py (~230 lines)
```

## Verification

- All 483 tests pass (no regressions)
- New test_sources.py: 19 tests, all GREEN
- file_id.py untouched — `_source_roots_for_version` duplication remains
  (it is used by `iter_rst_paths` / `classify_rst_and_md` for verify-side
   label building — removing it is out of scope for this issue)

## Verdict

✅ All changes are expected. No unintended files modified.
