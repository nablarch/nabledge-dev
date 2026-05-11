# Expert Review: Software Engineer — Task 21

**Date**: 2026-05-11
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: scripts/verify/verify.py, tests/ut/test_verify.py

## Summary

1 Finding — fixed before commit

## Findings

1. **docs-side anchor check had no unit test**
   - Violated clause: `.claude/rules/rbkc.md` §"Test coverage policy — verify": "All logic must have unit tests. Every new check added to verify requires a corresponding test before implementation (TDD)."
   - Description: The `elif anchor:` branch in the `if docs_md_text is not None:` block had no test that supplied a `docs_md_text` containing cross-doc links with anchors.
   - Fix: Added `test_docs_md_side_anchor_missing_fails` and `test_docs_md_side_anchor_exists_passes`. Fixed.

## Observations

- Dead `if target_md.exists():` guard inside docs-side `elif anchor:` branch (unreachable-false). Removed in the same commit.
- Misleading comment in `test_fail_anchor_missing_from_docs_md`. Fixed.

## Positive Aspects

- Dedup key expansion `(type_, category, file_id, anchor)` is correct and necessary.
- JSON-side guard `if target_md.exists():` correctly avoids false positives.
- `_heading_slugs_from_md` reused — no circular dependency.
