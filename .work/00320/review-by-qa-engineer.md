# Expert Review: QA Engineer

**Date**: 2026-05-11
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file (test_verify.py)

## Summary

0 Findings — shippable

## Findings

None.

## Observations

- `test_pass_local_label_no_file_id_skips_cross_doc_check` assertion `not any("missing-page" in i ...)` is narrower than needed; `assert issues == []` would be more precise.
- `test_fail_section_title_not_in_target_json` assertion `any("QL1" in i and "target-page" in i)` could be more precise by also checking section_title text appears in message.
- No MD-format cross-doc tests — consistent with implementation scope (MD branch does not call `_check_cross_doc_target`). Not a Finding.

## Positive Aspects

- All 313 tests pass with no regressions.
- Regression test `test_fail_different_labels_same_file_id_different_section_titles` precisely targets the hardest edge case (json_key dedup bug).
- PASS + FAIL paths covered for all four spec checks.
- Helper methods (`_write_json`, `_write_docs_md`, `_setup_dirs`) are well-factored.
- `test_pass_anchor_slug_matches_ascii_heading` calls `github_slug()` to derive anchor — avoids circular test.
- Dedup behavior tested on both JSON side and display-text :ref: paths.

## Files Reviewed

- tools/rbkc/tests/ut/test_verify.py (test code — 17 new test cases)
