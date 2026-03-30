# Expert Review: Prompt Engineer

**Date**: 2026-03-30
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The changes are well-targeted and address real behavioral problems in the pipeline. The constraints added to `fix.md` (E-1 through E-5) are specific and actionable. The severity assignment rules in `content_check.md` use a smart "state the wrong advice first" forcing function that produces more consistent results.

## Key Issues

### High Priority

1. **E-2 decision rule ambiguous for composite statements**
   - Description: "every word" phrasing could be over-restrictive, preventing valid multi-sentence synthesis
   - Suggestion: Change to "each distinct claim or fact" with explicit allowance for multi-sentence synthesis
   - Decision: Implement Now
   - Reasoning: Targeted fix that doesn't change intent but reduces misinterpretation

2. **E-1 and E-4 conflict without boundary definition**
   - Description: "outside the edited location" is unclear — adjacent sentences in same section vs other sections?
   - Suggestion: Clarify "edited location" = specific sentence/list item/code block; all other content in same section preserved verbatim
   - Decision: Implement Now
   - Reasoning: Ambiguity is a real gap that could cause continued adjacent-text corruption

### Medium Priority

1. **V3 format inconsistency (M-1)**
   - Description: V3 still uses inline `(severity: minor)` while V1/V2 no longer do
   - Suggestion: Update V3 to explicit severity sub-section format
   - Decision: Implement Now

2. **E-3 RST examples may be corrupted by markdown rendering (M-2)**
   - Description: Backtick-heavy inline examples may lose characters in markdown contexts
   - Suggestion: Wrap in fenced code block
   - Decision: Implement Now

3. **E-5 no fallback for prominent patterns (M-3)**
   - Description: No guidance when source has many consistent examples but no stated rule
   - Suggestion: Allow describing examples as "follow the form X" without stating it as a rule
   - Decision: Implement Now

### Low Priority

1. **L-1: Constraints at bottom without forward reference**
   - Decision: Defer to Future — modern LLMs process full prompt before acting; risk is low

2. **L-2: D-1 stability rule label is opaque**
   - Decision: Implement Now — naming explicitly in V1 costs one line and clarifies V2 back-reference

## Positive Aspects

- E-2 decision rule is a strong forcing function for preventing hallucination during omission fixes
- E-3's specific RST notation examples target exactly what LLMs tend to normalize away
- "State the wrong advice first" requirement in D-1 rule forces explicit impact reasoning before severity assignment
- E-1 is unambiguous: "no associated finding" as threshold is clear and binary
- Removing blanket `(severity: critical)` from V1/V2 headings correctly addresses the root cause of severity instability

## Recommendations

- Resolve E-1/E-4 boundary ambiguity before deploying — most likely source of continued adjacent-text corruption
- E-2 "each distinct claim or fact" clarification avoids over-restriction on valid synthesis
- Spot-check: test with a finding that touches RST notation within a list to verify E-3 and E-4 interact correctly

## Files Reviewed

- `tools/knowledge-creator/prompts/fix.md` (prompt)
- `tools/knowledge-creator/prompts/content_check.md` (prompt)
