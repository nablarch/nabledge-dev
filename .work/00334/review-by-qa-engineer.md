# Expert Review: QA Engineer

**Date**: 2026-05-14
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 test files

## Summary

1 Finding — fixed before PR creation

## Findings

**Finding 1: Bug 1 regression test was file-order-dependent**

- Violated clause: `.claude/rules/development.md` — "Bug-revealing cases: Input that exercises each specific failure mode. If a bug can occur, write a test that catches it."
- Description: `test_external_url_target_does_not_pollute_label_map` relied on `rglob` returning `link.rst` before `usage.rst`. If `usage.rst` came first, `setdefault` would register the real label first and the test would pass even without the fix.
- Fix applied: Added `_scan_rst_labels(link_rst)` scanner-level assertion that returns `[]` — fires unconditionally regardless of traversal order. Committed `b57e28bc9`.

## Observations

- `import textwrap` inside method body — module-level import already exists; cosmetic only.
- Removal of contradictory FAIL tests (`test_fail_rst_ref_quadrant4_dangling_is_ql1_fail` etc.) was correct — they had identical test data to PASS tests but opposite assertions.
- Q5 guard preserved in `test_fail_rst_ref_display_absent_entirely` — non-negotiable constraint met.
- Q3/Q4 docstrings accurately describe the five-quadrant spec logic.

## Positive Aspects

- Test fixture mirrors the real v1.4 regression scenario faithfully.
- Q5 guard intact and tested.
- All 555 unit tests pass.

## Files Reviewed

- `tools/rbkc/tests/ut/test_labels_doc_map.py` (test code)
- `tools/rbkc/tests/ut/test_verify.py` (test code)
