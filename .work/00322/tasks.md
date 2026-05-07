# Tasks: Move scan_sources and classify_sources to scripts/common/ for §2-2 compliance

**PR**: #329
**Issue**: #322
**Updated**: 2026-05-07

## Done

- [x] Created tasks.md — committed `a8c90fe71`
- [x] Task 1: Write TDD tests for scripts/common/sources module (RED) — committed `2a0881af1`
- [x] Task 2: Create scripts/common/sources.py (GREEN) — committed `2a0881af1`
- [x] Task 3: Update scripts/create/scan.py to re-export from scripts/common/sources — committed `571fd1c23`
- [x] Task 4: Update scripts/create/classify.py to re-export from scripts/common/sources — committed `571fd1c23`
- [x] Task 5: Update scripts/create/differ.py to import FileInfo from scripts/common/sources — committed `571fd1c23`
- [x] Task 6: Update scripts/run.py imports and run full test suite — committed `571fd1c23`
- [x] Task 7: Diff check and user confirmation before PR review request — diff-check.md created, all 483 tests pass
