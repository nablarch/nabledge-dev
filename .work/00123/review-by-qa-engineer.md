# Expert Review: QA Engineer

**Date**: 2026-03-30
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 3/5
**Summary**: The scenarios file covers core nabledge-1.3 functionality but contains known-failing assertions inherited from v1.4. These are intentionally kept for cross-version comparability with the v1.4 baseline.

## Key Issues

### High Priority

1. **Known-failing `.nabledge/` in output expectations**
   - Description: The `output` expectation includes `.nabledge/` in both ca-001 and ca-002. Known to fail in v1.4 (memory: "v1.4 全CA: `.nabledge/` がOutput検出に失敗").
   - Suggestion: Remove from both CA `output` arrays
   - Decision: Defer to Future
   - Reasoning: Kept for cross-version comparability with v1.4 baseline. Removing would make scores non-comparable between v1.3 and v1.4.

2. **`n:select` expectation in qa-001 likely absent from v1.3 RST**
   - Description: Memory notes `n:select は v1.4 RST に存在しないため期待値修正候補`. Same likely applies to v1.3.
   - Suggestion: Remove `n:select` from qa-001 expectations
   - Decision: Defer — track after baseline run
   - Reasoning: Will confirm via baseline run. If it consistently fails, remove in a follow-up issue.

### Medium Priority

3. **`-requestPath` (with dash) consistently fails**
   - Description: v1.4 qa-003: 3/4 (75%) because `-requestPath` (dash-prefixed) is not detected.
   - Suggestion: Remove `-requestPath`, keep `requestPath`
   - Decision: Defer — track after baseline run
   - Reasoning: Kept for cross-version comparability. Will address in follow-up.

4. **`getValidatorAction` in ca-002 sequence_diagram.messages**
   - Description: Known from v1.4 baseline that `getValidatorAction` doesn't appear in sequence diagram output.
   - Suggestion: Replace with `doHeader` or `doTrailer`
   - Decision: Defer — track after baseline run
   - Reasoning: Kept consistent with v1.4 for comparable baseline. Baseline run will confirm.

## Positive Aspects

- 5 QA scenarios cover distinct realistic use cases with no overlap
- Code analysis expectations are granular with 7 output section types
- Benchmark flags present and meaningful for cross-version comparison
- `class_diagram.relationships` assertions are specific and verifiable

## Recommendations

1. After baseline run, create GitHub Issues for the known-failing assertions to fix in a follow-up PR.
2. The `total_scenarios: 7` is manually maintained — risk of drift if scenarios change.

## Files Reviewed

- `.claude/skills/nabledge-test/scenarios/nabledge-1.3/scenarios.json` (configuration)
