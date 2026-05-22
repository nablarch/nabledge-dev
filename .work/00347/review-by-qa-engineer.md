# Expert Review: QA Engineer

**Date**: 2026-05-22
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: test_xlsx_common.py (NEW), test_verify.py (+6 tests), test_docs.py (+5 tests)

## Summary

0 Findings

## Findings

None.

## Observations

- **O1** — `test_docs.py` has a duplicate class name `TestReadmeUrlEncoding` (pre-existing, not introduced by this PR). The first class is silently shadowed; both carry identical methods so nothing is lost functionally.
- **O2** — `TestVerifyFileExcelP1Merged` in `test_verify.py` uses a different xlsx fixture column layout from the snippet in the review prompt (merges on column B vs A). Both are coherent with their respective data fixtures; no logic gap.
- **O3** — `TestBuildP1SectionsP1Merged.test_two_groups_two_rows_each` has minor assertion overlap with `test_data_rows_contains_all_rows` in the same class. Cosmetic only.
- **O4** — `_make_p1_merged_xlsx` in `test_xlsx_common.py` had an unused `get_column_letter` import. **Fixed in follow-up commit.**

## Positive Aspects

- TDD discipline is visible: every new behavior has a dedicated FAIL test alongside the PASS test.
- verify independence is correctly maintained — `TestVerifyFileExcelP1Merged` constructs xlsx fixtures from scratch with no imports from `xlsx_common.py`.
- QP check covers both directions: `test_qp_fail_section_count_equals_raw_row_count` catches the pre-fix regression, and `test_qp_pass_regular_p1_unaffected` guards that standard P1 is unaffected.
- Edge cases are thorough: single-row groups, mixed-size groups, all-empty tail rows, and `merge_groups=None` fallback.
- docs MD tests guard QO2 one-way containment for tail-row values.
- `_build_merge_groups` and `_read_title_col_merge_groups` are tested through real openpyxl xlsx fixtures with actual `merge_cells` calls.

## Files Reviewed

- `tools/rbkc/tests/ut/test_xlsx_common.py` (test code — NEW)
- `tools/rbkc/tests/ut/test_verify.py` (test code — MODIFIED)
- `tools/rbkc/tests/ut/test_docs.py` (test code — MODIFIED)
