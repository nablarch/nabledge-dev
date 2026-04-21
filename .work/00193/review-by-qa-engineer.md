# Expert Review: QA Engineer

**Date**: 2026-03-13
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 3/5
**Summary**: The test addresses a real regression risk with sound setup pattern. However, the E2E test does not directly exercise the `clean.py` fix — `kc_gen` (Python facade) does not call `clean.py`. A unit test for `clean.py` directly is needed to cover the actual regression path.

## Key Issues

### High Priority

1. **Test does not exercise the actual bug path (`clean.py` is never called)**
   - Description: `kc_gen` is a Python facade that does NOT call `clean.py`. `clean.py` is called only from `kc.sh`. The E2E test tests that `kc_gen` pipeline preserves pre-existing sources, but doesn't test the `clean.py` preserve/restore code path.
   - Suggestion: Add a unit test in `tests/ut/` that calls `clean_version` directly with a pre-existing `catalog.json` containing sources.
   - Decision: Implement Now
   - Reasoning: Critical coverage gap — the actual bug fix code path is untested.

### Medium Priority

2. **`commit` field not asserted, no explanation**
   - Description: `update_knowledge_meta` will update commits; test intentionally skips asserting commit but silently. A regression zeroing `commit` to `None` would pass silently.
   - Suggestion: Assert `actual["commit"] is not None` to guard against silent erasure.
   - Decision: Implement Now
   - Reasoning: Easy guard against regression.

3. **No assertion that `files` in resulting catalog is non-empty**
   - Description: If Phase A silently produces zero files, the sources-preservation test still passes, providing false confidence.
   - Suggestion: Add `assert len(catalog.get("files", [])) > 0`.
   - Decision: Implement Now
   - Reasoning: Cheap assertion, catches setup failures.

### Low Priority

4. **Pre-seeded catalog uses hardcoded `"files": []`**
   - Decision: Defer — already confirmed safe by `test_catalog_sources.py`.

## Positive Aspects

- Setup pattern (pre-seed catalog, run pipeline, assert post-state) is sound and consistent.
- Uses `version_fixture` parametrization, covering both v6 and v5.
- Correct use of `try/finally` for cleanup.
- Assertion messages are descriptive with expected vs actual values.

## Files Reviewed

- `tools/knowledge-creator/tests/e2e/test_e2e.py` (test file)
