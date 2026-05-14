# Expert Review: QA Engineer

**Date**: 2026-05-14
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files (scripts/verify/verify.py, tests/ut/test_verify.py)

## Summary

0 Findings (after resolution)

Original review: 3 Findings. After developer evaluation:
- Finding 1: Resolved as invalid (spec clause sanctions current behaviour)
- Finding 2(b): Fixed — `TestSheetToResultP2Subtypes` removed from test_verify.py
- Finding 3: Fixed — `test_fail_qc1_rst_severe_level_4_still_fails` now has real implementation

## Findings (all resolved)

### Finding 1: Excel QC4 classification at line 1660-1661 (RESOLVED — spec-sanctioned)
- **Reviewer's clause**: Condition 1 "verify has an implementation (no silent fallback, no unauthorized skip)"
- **Developer response**: §3-1 QC table explicitly marks QC4 Excel as `—` (out of scope). Line 1660-1661 handles the case where `any_occurrence=True, any_consumed=False` — a token that exists in JSON but behind `search_start`. Excel uses simplified bag-matching without sequential order tracking, so this is reported as QC1 (missing from expected forward position), which is correct per the spec. No QC4 for Excel.
- **Status**: Spec clause §3-1 table (QC4 Excel = —) sanctions current behaviour. Finding invalidated.

### Finding 2(b): TestSheetToResultP2Subtypes in test_verify.py (FIXED)
- **Violated clause**: `rbkc.md` — "create-side (converters, resolver, run, etc.) — No tests needed. verify passing is sufficient"
- **Fix**: Removed `TestSheetToResultP2Subtypes` class and `test_p2_4_load_sheet_subtype_map_parses_p2_4` (~130 lines, 7 tests) — committed `436798e`

### Finding 2(a): _rewrite_asset_links import (RESOLVED — intent preserved)
- **Reviewer's clause**: `rbkc.md` independence principle
- **Developer response**: The test docstring explicitly states: "This test imports docs._rewrite_asset_links ONLY inside the test, runs both on a matrix of inputs, and asserts equal output — catches drift between the two copies." This is a drift-detection test, not a dependency on create-side logic. The independence principle targets verify.py; the test intentionally cross-checks two independent implementations. Finding invalidated.

### Finding 3: pass body in test_fail_qc1_rst_severe_level_4_still_fails (FIXED)
- **Violated clause**: `rbkc.md` — "All logic must have unit tests"; `development.md` — "Every test class must include bug-revealing cases"
- **Fix**: Replaced `pass` with mock-based test that injects `(SEVERE/4)` warning into `rst_ast.parse` and asserts `UnknownSyntaxError` is raised, pinning the SEVERE/4 → FAIL policy — committed `436798e`

## Observations

- QO1 `_HEADING_RE` accepts `##` through `######` (levels 2–6), but JSON schema constrains to levels 2–4. Over-tolerance but not a spec violation since no clause restricts the heading level range in verify.
- `test_verify_and_docs_rewrite_agree_on_matrix` is a valuable drift-detection test that should remain.

## Positive Aspects

- QC1–QC4 for RST/MD is thoroughly tested with rotations, CJK tokens, and multi-section edge cases
- QC5 covers all format residue patterns (role, directive, raw HTML, escape chars) with both FAIL and PASS cases
- QL1/QL2 has strong edge-case coverage including invisible images, substitution-body exclusions, mailto/tel/anchor exclusions
- Excel P1 QP tests use real openpyxl-built .xlsx files (integration quality)
- verify.py has zero imports from `scripts.create.*` — independence principle correctly maintained in the implementation

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (implementation, 2386 lines)
- `tools/rbkc/tests/ut/test_verify.py` (tests, ~5170 lines after fixes)
