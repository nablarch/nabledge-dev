---
# Expert Review: Software Engineer

**Date**: 2026-03-31
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 7 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-targeted, focused change that addresses a real reliability problem with deterministic post-hoc enforcement. Implementation is generally solid with good test coverage.

## Key Issues

### Medium Priority

1. **Comment on new-section handling in `_apply_diff_guard` was ambiguous**
   - Description: "Remove any new sections added by the LLM that are not in scope" did not clarify that in-scope new sections are intentionally preserved
   - Suggestion: Clarify comment to mention both cases
   - Decision: Implement Now
   - Reasoning: Trivial, improves maintainability

2. **Silent `except Exception` in `check_one` discarded errors without logging**
   - Description: Phase D swallowed all LLM call exceptions without logging, making debugging difficult. Phase E already logs errors.
   - Suggestion: `except Exception as e: self.logger.error(f"check_one failed for {file_id}: {e}")`
   - Decision: Implement Now
   - Reasoning: Consistency with Phase E, important for observability

3. **`_extract_allowed_sections` early-exit lacked explanatory comment**
   - Description: The `break` on `no_knowledge_content_invalid` could mislead future maintainers
   - Suggestion: Add comment explaining full-rebuild bypass
   - Decision: Implement Now
   - Reasoning: Documentation only, trivial

### Low Priority

4. **Redundant `write_json` import alias in test_severity_flip.py**
   - Description: `from common import write_json as wj` inside test body when module-level import exists
   - Suggestion: Use module-level `write_json` directly
   - Decision: Implement Now
   - Reasoning: Trivial cleanup

5. **Non-zero returncode path in `fix_one` was implicit**
   - Description: The fallthrough after `if result.returncode == 0` was a bare `return {"status": "error"}` without context
   - Suggestion: Add explicit error message
   - Decision: Implement Now
   - Reasoning: Improves debuggability

6. **D-1 stability rule placement was ambiguous (between V2 and V3)**
   - Description: Reader could interpret it as a V2-only rule; it applies to all V1–V5 checks
   - Suggestion: Move to a top-level "General Rules" section before the checklist
   - Decision: Implement Now
   - Reasoning: Clear improvement to prompt readability

## Positive Aspects

- Deterministic enforcement: diff guard applied post-LLM, not reliant on LLM following instructions
- Full-rebuild bypass correctly gated to `no_knowledge_content_invalid` only
- Unit tests cover both functions in isolation, integration tests verify wiring
- E2E test adaptation is minimal and correct
- Module-level functions (`_extract_allowed_sections`, `_apply_diff_guard`) are independently testable
- Prompt rules (E-2, E-5, E-3) are precise and actionable with concrete decision rules

## Recommendations

- Consider a Phase D post-processor that freezes severity from round 1 forward (unless section content changed) to make D-1 deterministic rather than instructional
- Consider a distinct `"status": "no_change"` for the empty-fix case to help callers decide whether to retry

## Files Reviewed

- `scripts/phase_e_fix.py` (source code)
- `scripts/phase_d_content_check.py` (source code)
- `prompts/fix.md` (prompt)
- `prompts/content_check.md` (prompt)
- `tests/ut/test_diff_guard.py` (tests)
- `tests/ut/test_severity_flip.py` (tests)
- `tests/e2e/test_e2e.py` (tests)
