# Expert Review: QA Engineer (Phase 21-I)

**Date**: 2026-04-22
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files (verify.py, test_verify.py)

## Overall Assessment

**Rating (initial)**: 3/5 — fix is correct; initial tests left regression gaps.
**Rating (after fixes)**: 5/5 — additional tests added per recommendations below.

## Key Issues

### High Priority (Addressed)

1. **No direct `_json_text()` unit test** — initial tests exercised QL1 via `check_source_links` only. If future refactors move QL1 to different concat logic, pass-path tests could silently stop guarding top-level inclusion.
   - **Fix applied**: Added `TestJsonTextHelper` class with 4 tests:
     - `test_includes_title_and_top_level_content_and_sections` — pins concat contract
     - `test_excludes_hints` — confirms QC6 boundary
     - `test_missing_top_level_content_key_safe` — `.get()` KeyError safety
     - `test_empty_top_level_content_safe` — empty string edge case

2. **No regression FAIL test** — verify that QL1 still fires when content is genuinely missing.
   - **Fix applied**: Added `test_fail_rst_ref_missing_when_not_in_top_level_or_sections` — negative test confirming detection works when the fix's new code path does not silence it.

3. **MD top-level path untested** — initial 3 tests were RST-only.
   - **Fix applied**: Added `test_pass_md_internal_link_text_in_top_level_content`.

### Medium Priority (Addressed)

- Missing `"content"` key, empty content — both covered by `TestJsonTextHelper`.

### Low Priority (Not Addressed)

- ref display text / figure caption / literalinclude in top-level — not explicitly tested in isolation, but the direct `_json_text()` contract test guards the concat behavior universally, so no regression risk.

## Positive Aspects

- Fix is minimal and spec-aligned.
- Test data shape mirrors Phase 21-D output.
- Hints exclusion explicitly tested (QC6 boundary enforced).

## Recommendations

**Proceed after fixes applied.** All high/medium coverage gaps closed. 244 tests all PASS.

## Files Reviewed

- tools/rbkc/scripts/verify/verify.py (source code)
- tools/rbkc/tests/ut/test_verify.py (tests)
