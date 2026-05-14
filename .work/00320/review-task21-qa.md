# Expert Review: QA Engineer — Task 21

**Date**: 2026-05-11
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: tests/ut/test_verify.py

## Summary

2 Findings — both fixed before commit

## Findings

1. **JSON-side anchor FAIL not tested without docs_md_text**
   - Violated clause: `.claude/rules/development.md` — "Bug-revealing cases: If a bug can occur, write a test that catches it."
   - Description: All tests covering JSON-side FAIL path supplied `docs_md_text`, so a bug making the check conditional on `docs_md_text` would go undetected.
   - Fix: Added `test_fail_anchor_missing_no_docs_md_text`. Fixed.

2. **sections[].content anchor path had no coverage**
   - Violated clause: `.claude/rules/development.md` — "Bug-revealing cases: If a bug can occur, write a test that catches it."
   - Description: All new tests used `"sections": []`; a regression breaking anchor check in section content would pass all tests.
   - Fix: Added `test_fail_anchor_missing_in_section_content`. Fixed.

## Observations

- `test_fail_anchor_missing_from_docs_md` passes extraneous `docs_md_text` — no spec violation, comment clarified.
- Branch where target JSON exists but target docs MD is absent silently skips anchor check — intentional and correct per `elif` structure.

## Positive Aspects

- JSON-side and docs-side check paths properly separated into distinct tests.
- `test_dedup_same_file_different_anchors_checked_independently` pins the dedup-key design.
- `tmp_path` + `_setup()` pattern keeps boilerplate minimal.
