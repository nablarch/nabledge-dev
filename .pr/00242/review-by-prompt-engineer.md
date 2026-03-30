---
# Expert Review: Prompt Engineer

**Date**: 2026-03-30
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The change correctly removes keywords impossible to detect because they don't exist in source documentation. Restores the scenario to a meaningful, honest quality signal.

## Key Issues

### Medium Priority

1. **Keyword count reduced from 5 to 2 — coverage may be thin**
   - Description: Two keywords (`n:codeSelect`, `codeId`) test only that the AI mentions the tag name and attribute name. They don't verify that the AI explains *how* to use them or mentions related concepts. A skill could pass this benchmark by producing a minimal, low-quality answer.
   - Suggestion: Investigate RST docs for additional valid keywords (candidates: `codeListItem`, element name for option source). Add 1–2 keywords from the "how to use it" section of the RST.
   - Decision: Defer to Future
   - Reasoning: Valid concern, but adding new keywords requires RST research and baseline re-run. The existing open issue tracking scenario improvements is the correct vehicle. This PR's goal is specifically fixing broken expectations.

### Low Priority

1. **No rationale recorded in JSON for why keywords were removed**
   - Description: Someone reading `scenarios.json` six months from now won't know why qa-001 has only two expectations while others have four or five.
   - Suggestion: Add a `"note"` field or adjacent notes file explaining removal rationale.
   - Decision: Reject
   - Reasoning: Scenario JSON schema has no `note` field. Modifying the schema would be a separate non-trivial change. The reasoning is documented in the PR/commit history, which is the appropriate location.

## Positive Aspects

- Root cause verified empirically — keywords confirmed absent from RST before removal
- Identical fix applied to both v5 and v6 (consistent baselines)
- 100% detection rate with zero variance across 3 trials validates correctness
- Kept keywords (`n:codeSelect`, `codeId`) are the minimum necessary identifiers for the feature

## Recommendations

1. In a follow-up PR, investigate RST docs for 1–2 additional qa-001 keywords to strengthen discriminative power
2. Consider adding a `description`/`rationale` field to the scenario schema for long-term maintainability

## Files Reviewed

- `.claude/skills/nabledge-test/scenarios/nabledge-5/scenarios.json` (configuration/test)
- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json` (configuration/test)
