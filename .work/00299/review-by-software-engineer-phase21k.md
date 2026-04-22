# Expert Review: Software Engineer (Phase 21-K)

**Date**: 2026-04-22
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 11 files (tools/rbkc/ source + tests)

## Overall Assessment

**Rating**: 4.5/5
**Summary**: The refactor is clean, thorough, and correctly implements the content-only scope. All deleted hints infrastructure is verifiably gone from the production path, `generate_index` signature change is consistently propagated across all three call sites, and the `processing_patterns` fix correctly mirrors KC semantics (`phase_f_finalize.py:303`).

## Key Issues

### Medium Priority

1. **Stale `"hints": []` in test fixtures (151 occurrences)**
   - Description: `tools/rbkc/tests/ut/test_verify.py` contained 151 test JSON fixtures with `"hints": []`. Per `.claude/rules/rbkc.md`, RBKC JSON must not contain a `hints` field.
   - Decision: Implement Now
   - Fix applied: Stripped all 151 `"hints": []` occurrences; 202 tests still pass.

### Low Priority

1. **docs.py docstring drift**
   - Description: `tools/rbkc/scripts/create/docs.py` referenced stale path `scripts/index.py` and omitted `version` parameter in Public API.
   - Decision: Implement Now
   - Fix applied: Updated path to `scripts/create/index.py` and added `version: str = ""` to API signature.

2. **`_derive_type_category` coupling smell**
   - Description: Helper lives in `index.py` but its sole consumer is now `docs.py`; cross-module private import is mildly coupled.
   - Decision: Defer to follow-up
   - Reasoning: Non-blocking; both modules are in the same package. Keeping the helper where path-based derivation is semantically defined is acceptable.

## Positive Aspects

- Clean removal of `hints.py`, `constants.py`, and all derivative helpers — no orphaned imports.
- `generate_index` rewrite exactly matches KC's `phase_f_finalize.py:303` semantics.
- `test_no_hints_field_injected_into_pp` is a strong regression guard that encodes the pre-Phase-21-K bug.
- `verify.py` Public API docstring matches actual public functions (no stale entries).
- `run.py` docstring explicitly documents `content only; hints are out of RBKC scope` invariant.
- All three `generate_index` call sites (`create`, `update`, `delete`) consistently updated.

## Recommendations

- Address Medium fixture cleanup — done.
- Fix docstring drift — done.
- Consider moving `_derive_type_category` to `docs.py` in a follow-up.
- Verify `.work/00299/handoff-hints/` is referenced from the follow-up AI-hints issue.

## Files Reviewed

- tools/rbkc/scripts/create/index.py (source)
- tools/rbkc/scripts/create/docs.py (source)
- tools/rbkc/scripts/create/hints.py — DELETED
- tools/rbkc/scripts/common/constants.py — DELETED
- tools/rbkc/scripts/run.py (source)
- tools/rbkc/scripts/verify/verify.py (source)
- tools/rbkc/tests/ut/test_docs.py (tests)
- tools/rbkc/tests/ut/test_run.py (tests)
- tools/rbkc/tests/ut/test_verify.py (tests)
- tools/rbkc/tests/ut/test_hints.py — DELETED
- tools/rbkc/tests/ut/test_index.py (new tests)
