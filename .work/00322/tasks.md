# Tasks: Move scan_sources and classify_sources to scripts/common/ for §2-2 compliance

**PR**: #329
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
- [ ] Move `_source_roots` and `_all_releasenote_root` helpers to `sources.py`; remove duplicated `_source_roots_for_version` from `file_id.py` and delegate to `sources.py`
- [ ] Confirm tests pass GREEN

### Task 3: Update scripts/create/scan.py to re-export from scripts/common/sources
**Steps:**
- [ ] Replace `SourceFile` and `scan_sources` definitions with re-exports from `scripts.common.sources`
- [ ] Keep `_source_roots` as a pass-through for any callers that patch it in tests
- [ ] Confirm `test_file_id.py` TestReExportsFromCreate tests still pass

### Task 4: Update scripts/create/classify.py to re-export from scripts/common/sources
**Steps:**
- [ ] Replace `FileInfo` and `classify_sources` definitions with re-exports from `scripts.common.sources`
- [ ] Keep `_parent_prefix` backward-compat shim as-is
- [ ] Confirm tests pass

### Task 5: Update scripts/create/differ.py to import FileInfo from scripts/common/sources
**Steps:**
- [ ] Change `from scripts.create.classify import FileInfo` to `from scripts.common.sources import FileInfo`
- [ ] Confirm tests pass

### Task 6: Update scripts/run.py imports and run full test suite
**Steps:**
- [ ] Change `from scripts.create.scan import scan_sources` → `from scripts.common.sources import scan_sources`
- [ ] Change `from scripts.create.classify import FileInfo, classify_sources` → `from scripts.common.sources import FileInfo, classify_sources`
- [ ] Update patch paths in `test_run.py` if needed
- [ ] Run `cd tools/rbkc && python -m pytest tests/ -v` and confirm all pass

### Task 7: Diff check and user confirmation before PR review request
**Steps:**
- [ ] Run `git diff main...HEAD --stat` and `git diff main...HEAD` to enumerate all changed files
- [ ] Verify diff contains only expected changes (no unintended files)
- [ ] Output diff check result to `.work/00322/diff-check.md`
- [ ] Present result to user and get confirmation before requesting PR review

## Done

- [x] Created tasks.md — committed `a8c90fe71`
