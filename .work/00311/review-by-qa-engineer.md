# Expert Review: QA Engineer

**Date**: 2026-04-28
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 test files (test_docs.py, test_verify.py)

## Summary

0 Findings (1 Finding fixed before save: §3-4 test-class table updated)

## Findings

### Finding 1 (Fixed)

- **Violated clause**: `rbkc-verify-quality-design.md` §3-4: "新規チェック追加時にもこの表を更新し、設計書 ↔ テストの MECE を維持する"
- **Description**: 3 new test classes added to test_verify.py were not listed in the test-class traceability table.
- **Fix applied**: Added 3 rows to §3-4 table:
  - QO1 P2-1 p2_headings 逐次照合 → `TestCheckJsonDocsMdConsistency_QO1_P2Headings`
  - QO2 P2-1 per-line containment → `TestCheckJsonDocsMdConsistency_QO2_P2_1`
  - QO2 P2-3 hard line break normalization → `TestCheckJsonDocsMdConsistency_QO2_P2_3`

## Observations

- Dead assignment in `test_pass_exact_match` (first `docs` value immediately overwritten). Comment explains intent but unused value adds noise. No rule violation.
- `TestRenderXlsxP2Subtypes.test_p2_1_col0_becomes_h2` tests only fallback rendering (no `p2_raw_lines`). Primary path untested — acceptable per `rbkc.md` (create-side tests not required).
- `test_p2_1_generates_p2_headings` checks `p2_raw_lines` key presence but not content structure or `p2_base_col`. Acceptable given create-side tests are optional.

## Positive Aspects

- Complete verify logic coverage: all 5 new logic branches have unit tests
- All 401 tests pass with 0 regressions
- Edge cases properly included: wrong order, wrong level, wrong text, blank-line normalization chain
- Test isolation: production functions imported inside method bodies
- Assertions spec-anchored: `any("QO1" in i ...)` / `any("QO2" in i ...)` — stable under message reformatting

## Files Reviewed

- tools/rbkc/tests/ut/test_docs.py (tests)
- tools/rbkc/tests/ut/test_verify.py (tests)
