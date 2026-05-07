# Tasks: Move scan_sources and classify_sources to scripts/common/ for §2-2 compliance

**PR**: (TBD)
**Issue**: #322
**Updated**: 2026-05-07

## Not Started

### Task 1: Write TDD tests for scripts/common/sources module (RED)
**Steps:**
- [ ] Create `tests/ut/test_sources.py` with failing tests that import `scan_sources`, `classify_sources`, `SourceFile`, `FileInfo` from `scripts.common.sources`
- [ ] Confirm RED (ImportError)

### Task 2: Create scripts/common/sources.py (GREEN)
**Steps:**
- [ ] Create `scripts/common/sources.py` with `SourceFile` (dataclass), `scan_sources`, `FileInfo` (dataclass), `classify_sources`, `_sheet_slug`
- [ ] Move `_source_roots` and `_all_releasenote_root` helpers to `sources.py` (replacing the duplicated `_source_roots_for_version` in file_id.py with a reference to `sources.py`, or vice versa — keep single source of truth)
- [ ] Confirm tests pass GREEN

### Task 3: Update scripts/create/scan.py to re-export from scripts/common/sources
**Steps:**
- [ ] Replace `SourceFile` and `scan_sources` definitions with re-exports from `scripts.common.sources`
- [ ] Keep `_source_roots` and `_all_releasenote_root` as pass-through re-exports or delegates (test_file_id.py references `scripts.create.scan._source_roots` in tests/ut/test_run.py patch targets)
- [ ] Confirm `test_file_id.py` TestReExportsFromCreate tests still pass

### Task 4: Update scripts/create/classify.py to re-export from scripts/common/sources
**Steps:**
- [ ] Replace `FileInfo` and `classify_sources` definitions with re-exports from `scripts.common.sources`
- [ ] Keep `_parent_prefix` backward-compat shim as-is (already delegates to common)
- [ ] Confirm tests pass

### Task 5: Update scripts/create/differ.py to import FileInfo from scripts/common/sources
**Steps:**
- [ ] Change `from scripts.create.classify import FileInfo` to `from scripts.common.sources import FileInfo`
- [ ] Confirm tests pass

### Task 6: Update scripts/run.py imports and run full test suite
**Steps:**
- [ ] Change `from scripts.create.scan import scan_sources` → `from scripts.common.sources import scan_sources`
- [ ] Change `from scripts.create.classify import FileInfo, classify_sources` → `from scripts.common.sources import FileInfo, classify_sources`
- [ ] Update patch paths in `test_run.py` if needed (`scripts.run.scan_sources` / `scripts.run.classify_sources` mock targets should still work as they patch run.py's namespace)
- [ ] Run `cd tools/rbkc && python -m pytest tests/ -v` and confirm all pass

## Done

- [x] Created tasks.md
