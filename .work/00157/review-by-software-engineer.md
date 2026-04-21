# Expert Review: Software Engineer

**Date**: 2026-03-10
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 8 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The PR cleanly externalizes hardcoded Python mapping constants to per-version JSON files. The design is appropriate, and E2E tests now run parametrically against both v5 and v6.

## Key Issues

### Medium Priority

1. **Silent failure on missing mapping file**
   - Description: `_load_mappings()` returned empty defaults when the mapping file was absent, masking mistakes (wrong path, forgotten JSON file).
   - Suggestion: Raise `FileNotFoundError` with a clear message pointing to the correct file to create.
   - Decision: Implement Now
   - Reasoning: Easy fix, significantly improves error UX for future version additions.

2. **No JSON schema validation for mapping files**
   - Description: Typos in JSON keys (e.g., `"patterns"` instead of `"pattern"`) cause confusing `KeyError` tracebacks.
   - Suggestion: Add minimal key validation in `_load_mappings()`.
   - Decision: Defer to Future
   - Reasoning: Adds complexity; current naming is clear enough and the risk is low for a small team.

3. **`generate_expected.py` `main()` hardcodes version "6"**
   - Description: CLI entrypoint `python generate_expected.py <repo> <output>` always generates v6 expected values regardless of the version being tested.
   - Suggestion: Add optional `[version]` argument, defaulting to "6".
   - Decision: Implement Now
   - Reasoning: Small, isolated fix; prevents silently wrong data if someone regenerates expected values for v5.

### Low Priority

4. **Missing v5 test for `extension_components/` patterns**
   - Description: The v5-specific ETL/report/workflow extension paths are v5's primary structural difference but had no test coverage.
   - Suggestion: Add a test verifying `extension_components/etl/` maps to `extension/etl`.
   - Decision: Implement Now
   - Reasoning: Trivial to add; improves confidence in v5-specific mappings.

5. **Duplication between `_load_mappings()` and `load_mappings()`**
   - Description: Near-identical function bodies in `step2_classify.py` and `generate_expected.py` could diverge silently.
   - Suggestion: Add cross-reference comments in both copies.
   - Decision: Implement Now
   - Reasoning: One-line comment prevents future divergence.

## Positive Aspects

- Per-version complete mapping files (not a shared base + overrides) is the right design for order-sensitive RST patterns.
- `version_fixture` parametrization in `test_e2e.py` eliminates duplicate test classes cleanly.
- Error message in `Step2Classify` now correctly references the version-specific JSON file.
- Unit test `test_excel_classification.py` correctly copies mappings directory into temp repos.

## Recommendations

- Consider adding a `README` or comment block to `mappings/` explaining the expected JSON structure and the order-sensitivity of RST patterns.
- Track JSON schema validation (#2) as a follow-up issue.

## Files Reviewed

- `tools/knowledge-creator/mappings/v5.json` (configuration)
- `tools/knowledge-creator/mappings/v6.json` (configuration)
- `tools/knowledge-creator/scripts/step2_classify.py` (source code)
- `tools/knowledge-creator/scripts/step1_list_sources.py` (source code)
- `tools/knowledge-creator/tests/e2e/generate_expected.py` (tests)
- `tools/knowledge-creator/tests/e2e/test_e2e.py` (tests)
- `tools/knowledge-creator/tests/ut/test_excel_classification.py` (tests)
- `tools/knowledge-creator/tests/ut/test_unmatched_error.py` (tests)
