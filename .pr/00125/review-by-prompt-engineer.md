# Expert Review: Prompt Engineer

**Date**: 2026-03-06
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: The constraint is effective and well-justified with measurable impact data. The instruction is clear and uses strong visual markers (CRITICAL label, bold formatting). However, there are opportunities to improve agent guidance through more specific actionable instructions and stronger enforcement mechanisms.

## Key Issues

### High Priority

None identified.

### Medium Priority

1. **Insufficient guidance on "how" to execute as single operation**
   - **Description**: The constraint tells agents what NOT to do ("DO NOT split") but doesn't clearly explain HOW to construct content in memory and write in one step. Agents may understand the prohibition but still struggle with the correct execution pattern.
   - **Suggestion**: Add explicit execution pattern after line 525:
     ```markdown
     **How to execute as single operation**:
     1. Build complete document content in a variable/memory
     2. Include all sections from Step 3.5 item 2 (8 placeholders)
     3. Verify compliance internally (Step 3.5 item 3)
     4. Call Write tool once with complete content
     5. Verify Write succeeded before proceeding
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: Current constraint has proven effective (77% token reduction achieved). The existing workflow steps 1-4 already provide this guidance implicitly. Adding explicit "how-to" may be redundant since the constraint fixes the specific pathology (splitting Build/Write). Monitor for any future violations before adding complexity.

2. **Token impact explanation could be more visual**
   - **Description**: Line 525 explains "multiplying token usage by 2-3x" in text, but the actual case showed 7x multiplication (7,700 → 53,900). The dramatic impact could be more visually emphasized to reinforce why this constraint is CRITICAL.
   - **Suggestion**: Add concrete example after line 525:
     ```markdown
     **Real impact example** (ca-004 incident):
     - Correct (single step): 12,256 tokens
     - Incorrect (split steps): 53,900 tokens (7x multiplication!)
     - Cause: Each split re-reads 11.5K token content as input
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: The constraint is already effective without the example. Adding incident-specific data may date quickly and requires maintenance. The general principle ("2-3x" multiplier with "causes re-read" explanation) is sufficient for agent understanding. Consider adding if violations recur.

3. **Missing verification checkpoint after constraint**
   - **Description**: The constraint prohibits splitting but doesn't add a verification step to confirm compliance. Agents might accidentally violate the constraint without realizing it until token usage is reviewed.
   - **Suggestion**: Add verification bullet to existing Step 3.5 item 4 validation checkpoint (line 543-550):
     ```markdown
     - Build and Write executed as single operation (no intermediate tool calls)
       - **If violated**: Review constraint at line 522, rebuild in memory, HALT workflow
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: The validation checkpoint at lines 543-550 focuses on Write operation outcomes (success, path, file size), not process compliance. Adding process verification here mixes concerns. The constraint's bold CRITICAL label and multi-line explanation should be sufficient for agent attention. If violations recur, consider adding a separate process compliance check earlier in the step.

### Low Priority

1. **Constraint placement could be more prominent**
   - **Description**: The constraint appears at line 522, after the "Important" note about diagrams (line 520) and before the "Verify template compliance" section (line 527). While it's marked CRITICAL, it's embedded within a sequence of instructions rather than at the step header where agents scan first.
   - **Suggestion**: Consider moving the constraint to immediately after the Step 3.5 heading (after line 489) as a prerequisite note, similar to how Step 0 emphasizes start time recording as CRITICAL. This ensures agents see it before processing any sub-steps.
   - **Decision**: Reject
   - **Reasoning**: The current placement (line 522) is contextually optimal - it appears exactly where agents need it, right before the Build/Verify/Write sequence (steps 2-4). Placing it at the step header (line 489) would separate it from its application context by 30+ lines, reducing effectiveness. The CRITICAL label and bold formatting provide sufficient prominence. Step 0's placement works because it's a prerequisite for the entire workflow; this constraint is specific to items 2-4 of Step 3.5.

## Positive Aspects

- **Strong visual markers**: "CRITICAL" label and bold formatting effectively draw agent attention
- **Clear prohibition**: "DO NOT split Build and Write" is unambiguous
- **Concrete scope**: Specifies exactly which items (2, 3, 4) must be continuous
- **Justification provided**: Explains the consequence (2-3x token multiplication) and root cause (content re-read)
- **Measurable impact**: The fix achieved 77% token reduction (53,900 → 12,256), validating the constraint's effectiveness
- **Consistent pattern**: Uses similar structure to existing "CRITICAL SEQUENCING" instruction at line 554, maintaining workflow consistency

## Recommendations

1. **Monitor for violations**: Track whether agents respect this constraint in future code-analysis workflow executions. If violations occur, escalate from Medium to High priority and implement the "how-to" guidance and verification checkpoint.

2. **Consider workflow-wide audit**: Check if similar Build/Write patterns exist in other workflows (knowledge-search.md, etc.) where content generation and file writing might be split. Apply similar constraints proactively if found.

3. **Document in post-mortem**: Ensure the ca-004 post-mortem (if it exists) cross-references this constraint as the implemented prevention measure, creating traceability between incident and fix.

4. **Horizontal check**: Verify that other multi-step content generation patterns in the workflow don't have similar token inflation risks. Lines 554 (CRITICAL SEQUENCING for time calculation) shows awareness of similar issues.

## Files Reviewed

- `.claude/skills/nabledge-6/workflows/code-analysis.md` (workflow definition)
