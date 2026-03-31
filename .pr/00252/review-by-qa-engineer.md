# Expert Review: QA Engineer

**Date**: 2026-03-31
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The changes replace non-deterministic LLM-based verification with a clean, deterministic script pipeline. Unit tests cover the four primary code paths well. Minor issues addressed: `grep -qF` fix for regex safety, cleanup of 0-hit test mock, added two additional test scenarios (read-sections empty output, v1.4 path construction).

## Key Issues

### Medium Priority

1. **`grep -q` regex metacharacter risk**
   - Description: Keywords passed directly to `grep -q` could be misinterpreted as regex (e.g. `.`, `*`, `[`)
   - Suggestion: Use `grep -qF` for fixed-string matching
   - Decision: Implement Now
   - Reasoning: `n:codeSelect` is currently safe (`:` is not a regex metachar) but defensive fix prevents future breakage

2. **`read-sections.sh` empty output path not tested**
   - Description: No test for when search finds hits but read-sections returns empty content
   - Suggestion: Add test scenario with search hit but empty read output
   - Decision: Implement Now
   - Reasoning: This is a distinct code path from keyword-missing (partial content)

### Low Priority

3. **0-hit test had unnecessary `read-sections.sh` mock**
   - Description: Mock was created but never reached due to early return
   - Suggestion: Remove the mock to clarify test intent
   - Decision: Implement Now
   - Reasoning: Makes test intent clearer; no logic change

4. **No test for non-6 version path construction**
   - Description: Only version `"6"` tested; `nabledge-1.4` path never exercised
   - Suggestion: Add v1.4 test scenario
   - Decision: Implement Now
   - Reasoning: Low effort, confirms path construction for `nabledge-1.4`

5. **`jq` dependency check lacked explanation**
   - Description: Comment didn't explain why jq is needed
   - Suggestion: Clarify that jq is used by `full-text-search.sh` and `read-sections.sh`
   - Decision: Implement Now
   - Reasoning: `full-text-search.sh` uses jq internally for JSON parsing

## Positive Aspects

- Sourcing guard (`NABLEDGE_TEST_SOURCE_ONLY=1`) is elegant and minimal
- Four test scenarios map directly to four distinct code paths
- Mock scripts use `<<'MOCK'` heredoc quoting — no variable interpolation surprises
- Output capture with `mktemp` avoids subshell variable scoping issues
- Comment at lines 392-393 explicitly links checks to nabledge-test benchmark scenarios (`qa-002`/`qa-001`)
- All 20 dynamic check calls properly uncommented and mapped to correct versions/tools

## Recommendations

- Consider adding integration-level smoke test that runs the actual scripts against the installed test environments (separate from unit tests)

## Files Reviewed

- `tools/tests/test-setup.sh` (test infrastructure)
- `tools/tests/test-verify-dynamic.sh` (unit tests)
