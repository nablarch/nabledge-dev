# Expert Review: QA Engineer

**Date**: 2026-03-10
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: The changes add meaningful content assertions to an existing integration test and introduce a well-targeted new unit test for the multiple-URL rendering path. Coverage of the key new behaviors is solid, with a few minor gaps addressed after review.

## Key Issues

### Medium Priority

1. **No test for zero `official_doc_urls` (empty list)**
   - Description: Neither the existing tests nor the new test verifies that a knowledge file with `"official_doc_urls": []` produces output without a `**公式ドキュメント**` line.
   - Suggestion: Add a test with empty `official_doc_urls` asserting the line is absent.
   - Decision: Implement Now — added `test_docs_empty_official_urls_and_hints` covering both empty URLs and empty hints.

2. **New test duplicates boilerplate classified dict construction**
   - Description: The `classified` dict is copy-pasted verbatim across 5 tests.
   - Decision: Defer to Future — pre-existing issue, out of scope.

### Low Priority

3. **Hints assertion doesn't cover single-hint case**
   - Description: No test for `hints: ["single"]` producing no trailing comma.
   - Decision: Defer to Future — `join` on one element is trivially correct, not worth adding now.

4. **`test_merge_then_resolve_then_docs` now tests two concerns**
   - Description: Integration test now also validates formatting rules.
   - Decision: Reject — the formatting assertions are inexpensive and the integration context is valuable.

## Positive Aspects

- Assertion strings exactly match production code output, making regressions immediately visible.
- `test_docs_multiple_official_urls` is narrowly scoped with minimal setup.
- Hints assertions in `test_merge_then_resolve_then_docs` reflect per-section structure correctly.
- New test correctly uses no `split_info`, matching the realistic non-split code path.
- `mock_claude` fixture ensures deterministic tests without real Claude CLI calls.

## Recommendations

- The pattern of asserting rendered output content (not just file existence) is correct for this layer — continue applying it to other Phase M/F output assertions.

## Files Reviewed

- `tools/knowledge-creator/tests/ut/test_phase_m.py` (tests)
