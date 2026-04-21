# Expert Review: Software Engineer — Session 37 Top-Level Hints

**Date**: 2026-04-22
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: run.py, docs.py, index.py, verify.py, test_run.py, test_verify.py, test_docs.py, rbkc-json-schema-design.md

## Overall Assessment

**Rating**: 4.5/5
**Summary**: Implementation cleanly extends the Phase 21-H array-form hints pipeline to file-level units. The `__file__` sentinel is handled symmetrically across create/verify, tests cover the essential boundaries, and verify remains independent of create-side internals.

## Key Issues

### Medium Priority

**M1. Sentinel constant duplicated with divergent names**
- Description: `run.py` defined `_FILE_SENTINEL` and `verify.py` independently defined `_TOP_LEVEL_HINTS_KEY` — same literal, two names.
- Suggestion: Extract to `scripts/common/constants.py` as `FILE_SENTINEL`, import from both sides.
- Decision: **Implement Now** — small, no behaviour change, removes rename-drift risk.

### Low Priority

**L1. `_pop_top_level_hints` empty-string edge case**
- Description: If `top_title == ""` and head title also `""`, popping happens on a weak signal.
- Decision: **Defer** — not an observed issue in current data; would only matter for malformed hints files.

**L2. docs.py ordering matches spec** — no change needed.

**L3. `_parse_docs_md_hints` key collision if section literally titled `__file__`**
- Decision: **Defer** — extremely unlikely in real data; documented convention.

## Positive Aspects

- Clean separation between create-side (run.py) and verify — no cross-imports.
- TDD discipline evident: RED→GREEN cycles verified for each new check.
- `index[]` determinism preserved per schema §2-3 invariants.
- Symmetric fallback: `existing_hints` applies to top-level hints too.

## Changes Applied

- M1: Created `tools/rbkc/scripts/common/constants.py` with `FILE_SENTINEL`. Both run.py and verify.py import from there.
