# Expert Review: Software Engineer (Implementation)

**Date**: 2026-04-28
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 8 files (xlsx_common.py, xlsx_releasenote.py, xlsx_security.py, docs.py, run.py, verify.py, test_docs.py, test_verify.py)

## Summary

0 Findings

## Findings

None.

## Observations

- Return type annotation for `_build_p2_1_meta` declares a 2-tuple but function returns 3 values (`p2_headings, p2_raw_lines, base_col`). Correct annotation: `tuple[list[dict], list[list[tuple[int, str]]], int]`. No spec clause violated — maintainability note only.
- `import re` inside function body in `load_sheet_subtype_map`. Moving to module level would align with codebase style. No correctness impact.
- `TestRenderXlsxP2Subtypes.test_p2_1_col0_becomes_h2` exercises only the fallback P2-1 rendering path (no `p2_raw_lines`). Primary path (with `p2_raw_lines`) untested in unit tests — acceptable per `rbkc.md` (create-side tests not required).
- P2-1 heading rows with sibling body cells at col≥3 in same row: sibling content not rendered in docs MD, but none of the 16 actual P2-1 sheets trigger this. Latent structural gap, not active defect.

## Positive Aspects

- Architecture cleanly layered: xlsx_common (create-side) and verify fully independent
- verify correctly kept as quality gate: QO1/QO2 checks tighten coverage, not weakened
- TDD compliance for verify: all new checks have unit tests
- `load_sheet_subtype_map` regex correctly handles header/separator/P1/P2-2 rows
- All 401 tests pass

## Files Reviewed

- tools/rbkc/scripts/create/converters/xlsx_common.py (source code)
- tools/rbkc/scripts/create/converters/xlsx_releasenote.py (source code)
- tools/rbkc/scripts/create/converters/xlsx_security.py (source code)
- tools/rbkc/scripts/create/docs.py (source code)
- tools/rbkc/scripts/run.py (source code)
- tools/rbkc/scripts/verify/verify.py (source code)
- tools/rbkc/tests/ut/test_docs.py (tests)
- tools/rbkc/tests/ut/test_verify.py (tests)
