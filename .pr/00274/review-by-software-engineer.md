# Expert Review: Software Engineer

**Date**: 2026-04-10
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 3 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured refactoring that successfully implements per-section fix strategy and severity locking. Architecture is sound with clear separation of concerns. Two bugs fixed post-review (prior_hash None check, location normalization in persistent_findings tracking). Minor issues around logging and code deduplication remain as future improvements.

## Key Issues

### High Priority

1. **Prior hash None check in `_lock_severity()`**
   - Description: `if prior_hash and ...` silently skips severity lock when `_section_hash` field is missing from older prior findings (empty string falsy)
   - Suggestion: `if prior_hash is not None and prior_hash and current_hash == prior_hash:`
   - Decision: Implement Now
   - Reasoning: Semantic correctness fix; empty string from `.get("_section_hash", "")` default would incorrectly skip lock

2. **Persistent findings tracking uses raw location strings**
   - Description: `run.py` tracks `(file_id, location, category)` with raw location, but `phase_d_content_check.py` normalizes with `_normalize_finding_location()`. If locations differ by case ("s1" vs "S1"), same finding is tracked as separate entries, preventing retry limit from triggering
   - Suggestion: Apply same normalization (`\bs(\d+)\b` regex) before creating persistent_findings keys
   - Decision: Implement Now
   - Reasoning: Logic bug that could cause retry limit to never trigger if LLM varies location casing

### Medium Priority

3. **`_group_findings_by_section()` missing type hints**
   - Decision: Defer
   - Reasoning: Dev tool with good test coverage; type hints are nice-to-have not blocking

4. **Clean history persistence not unit tested**
   - Decision: Defer
   - Reasoning: History is optimization-only (not correctness-critical); loss resets counts to 0 which is safe

5. **`_run_final_verification()` scoping comment unclear**
   - Decision: Defer
   - Reasoning: Code works correctly; comment is clear enough for current maintainers

### Low Priority

- Location normalization duplicated in phase_d and phase_e → Defer (refactor to common.py in future PR)
- Missing granular logging for section fix → Defer

## Positive Aspects

- Per-section fix strategy cleanly isolates LLM context to target section, structurally preventing mutations to other sections
- Hash-based severity lock is solid approach to prevent D-1 reversals
- `_group_findings_by_section()` separation is elegant — structural findings still use full-knowledge fix path
- Retry limit (persistent findings exclusion) prevents infinite cycling on unfixable issues
- Final verification scoping ensures cost-efficient targeted re-check

## Files Reviewed

- `tools/knowledge-creator/scripts/phase_d_content_check.py` (severity locking)
- `tools/knowledge-creator/scripts/phase_e_fix.py` (per-section fix)
- `tools/knowledge-creator/scripts/run.py` (pipeline orchestration)
