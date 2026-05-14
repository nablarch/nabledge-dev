# Expert Review: QA Engineer

**Date**: 2026-05-14
**Reviewer**: AI Agent as QA Engineer (bias-avoidance)
**Checks Reviewed**: QO1 section level (Phase 22-B-16a), QP P1 column-value pairing (§3-4)

## Summary

1 Finding resolved — 0 Findings remaining

## Findings

### Finding 1 (Resolved): `pair_extra` path in `check_xlsx_p1_pairing` had no unit test

- **Violated clause**: `.claude/rules/rbkc.md` §テストカバレッジポリシー — "verify のすべてのロジックにはユニットテストが必要"
- **Description**: The `pair_extra` code path (verify.py L1588–1595) — fires when JSON section contains a `{列名}: {値}` line whose column name is absent from the Excel header — had no direct unit test. The only indirect coverage was through `verify_file` asserting on QC2, which would pass even if the QP branch were deleted.
- **Fix applied**: Added `test_fail_pair_extra_column_not_in_header` to `TestCheckXlsxP1Pairing`. Asserts `any("[QP]" in i and "unexpected" in i for i in issues)`. GREEN confirmed.

## Observations

- `_parse_section_pairs` has no standalone test, but its behavior is covered via the public `check_xlsx_p1_pairing` tests. Acceptable for a private helper.
- No test explicitly asserts P1 JSON does not trigger a spurious QO1 level FAIL, but no spec clause requires it.
- `used_idx` logic in QO1 level check handles duplicate section titles correctly; no spec clause mandates a test for this edge case.

## Positive Aspects

- QO1 level check integrates cleanly into `check_json_docs_md_consistency` without duplicating the heading scan loop.
- All 6 `TestCheckJsonDocsMdConsistency_QO1_Level` test cases are spec-derived (not implementation mirrors).
- `test_fail_swapped_values_across_rows` documents the exact gap QP closes (bag matching cannot catch swapped values).
- `duplicate_column` FAIL path has a dedicated test in `TestVerifyP1DuplicateColumnNames`.

## Verify Results (all 5 versions)

- v6: All files verified OK
- v5: All files verified OK
- v1.4: All files verified OK
- v1.3: All files verified OK
- v1.2: All files verified OK
