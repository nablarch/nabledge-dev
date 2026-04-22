# Expert Review: QA Engineer (Phase 21-K)

**Date**: 2026-04-22
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 5 test files + index.py under test

## Overall Assessment

**Rating**: 4.5/5
**Summary**: Test coverage for the Phase 21-K scope change and the `processing_patterns` bug fix is solid and well-targeted. One meaningful gap in the regression guard, plus a few minor edge cases, addressed in-commit.

## Key Issues

### Medium Priority

1. **`test_no_keywords_block_emitted` did not exercise the hints code path**
   - Description: Original fixture contained no `hints` field, so the pre-Phase-21-K buggy implementation would have produced the same output — test would pass trivially.
   - Decision: Implement Now
   - Fix applied: Replaced with two distinct tests (`test_top_level_hints_field_must_not_render_keywords_block` and `test_section_hints_field_must_not_render_keywords_block`) that inject stray `hints` at top level and section level respectively, asserting absence of `<details>`, `<summary>keywords</summary>`, and the keyword strings.

### Low Priority

1. **`test_no_hints_field_injected_into_pp` assertion strength**
   - Description: Original test only asserted `pp == ""` and keyword absence. A buggy implementation could still mis-assign `type`/`category` columns.
   - Decision: Implement Now
   - Fix applied: Added assertions on `type` and `category` columns.

2. **`generate_index` edge cases uncovered**
   - Description: No tests for empty `file_infos` (header-only output) or sort-determinism for multiple entries.
   - Decision: Implement Now
   - Fix applied: Added `TestGenerateIndexEdgeCases` with `test_empty_file_infos_yields_header_only` and `test_entries_sorted_by_path`.

3. **Lingering `"hints": []` in test_verify.py fixtures**
   - Description: 151 inert but misleading fixtures.
   - Decision: Implement Now (aligns with SE Medium finding)
   - Fix applied: Stripped in the same commit.

## Positive Aspects

- `TestProcessingPatternsSemantics` encodes the spec from index.py's docstring (three distinct type cases).
- `test_no_hints_field_injected_into_pp` is a real regression guard — injects stray hints that the buggy implementation would have leaked.
- `TestMissingJsonSkipped` covers the failed-conversion path without crashing.
- `TestTitleCommaEscape` covers a TOON-format-breaking edge case with positive and negative assertions.
- `_FakeFI` dataclass keeps tests decoupled from full `FileInfo` machinery.
- 202 tests passing + live verify GREEN confirms integration correctness beyond unit scope.

## Recommendations

- All identified issues addressed in the same commit.
- No follow-up testing debt identified.

## Files Reviewed

- tools/rbkc/tests/ut/test_index.py (new)
- tools/rbkc/tests/ut/test_docs.py (modified)
- tools/rbkc/tests/ut/test_run.py (modified)
- tools/rbkc/tests/ut/test_verify.py (modified)
- tools/rbkc/scripts/create/index.py (code under test)
