# Expert Review: QA Engineer (Phase A)

**Date**: 2026-05-15
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files (test_read_sections.py, test_keyword_search.py)

## Summary

2 Findings — fixed in `819677fe9`

## Findings

1. **Path traversal rejection untested**
   - Violated clause: `.claude/rules/development.md` — "Bug-revealing cases: If a bug can occur, write a test that catches it"
   - Description: `read-sections.sh` has a path traversal guard but no test exercised it
   - Fix: Added `test_path_traversal_rejected` and `test_absolute_path_rejected` tests

2. **No-arguments call untested**
   - Violated clause: `.claude/rules/development.md` — "Edge cases: empty inputs"
   - Description: Script exits 1 with Usage message on no args, but no test covered this
   - Fix: Added `test_no_arguments` test

## Observations

- `_run` helper discards returncode/stderr — adequate for happy-path tests but error-path tests call `subprocess.run` directly (consistent with `test_keyword_search.py` pattern)

## Positive Aspects

- Test class names clearly document intent
- Assertions are specific (exact strings, Japanese content, delimiter checks)
- Fixture design is clean and self-contained
- All 27 tests pass in 0.56s

## Files Reviewed

- tools/tests/test_read_sections.py (test code)
- tools/tests/test_keyword_search.py (SCRIPT_PATH change only)
