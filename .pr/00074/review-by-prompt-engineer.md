# Expert Review: Prompt Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The changes significantly improve clarity and completeness of PR title generation instructions. The addition of explicit rules, process steps, and edge case handling provides excellent guidance for agent behavior. Minor improvements needed in instruction flow and potential edge case handling.

## Key Issues

### High Priority

**None identified** - The changes are functional and provide clear guidance.

### Medium Priority

1. **Potential truncation confusion in multi-step process**
   - Description: The title generation process describes truncation in step 3, but the actual truncation logic (when and how to truncate) could be clearer. The example shows truncation happening mid-sentence, but there's no guidance on whether to truncate at word boundaries or how to handle very short descriptions.
   - Suggestion: Add explicit guidance: "When truncating, prefer breaking at word boundaries. Minimum description length should be at least 20 characters before issue number. If base description is too short (<10 chars), reconsider title generation."
   - Decision: **Reject** - The current implementation uses `truncate_title()` function which already handles word boundaries correctly. The workflow correctly instructs to use this function, so adding explicit guidance would duplicate what the code already does.

2. **Missing guidance on issue number extraction failure**
   - Description: The "Issue Number Handling" section states issue number is "always extracted from branch name" but doesn't address what happens if extraction fails (malformed branch name, no issue number in branch).
   - Suggestion: Add fallback behavior: "If issue number cannot be extracted from branch name (format: `{number}-{description}`), prompt user or check if issue was provided in step 1. Title format without issue number: `<type>: <description>` as fallback."
   - Decision: **Implement Now** - Valid edge case. Implemented fallback behavior that continues without issue number if extraction fails (changed from exit to warning).

3. **Example truncation calculation inconsistency**
   - Description: The truncation example shows 76 chars → 62 chars (14 char reduction), but the math doesn't clearly show where the "..." (3 chars) fits in the calculation. It's slightly confusing to validate.
   - Suggestion: Break down the example: "Original: 'feat: Add comprehensive JWT authentication middleware with refresh tokens (#123)' (76 chars) → Remove 'middleware with refresh tokens' (31 chars) → Add '...' (3 chars) → Final: 'feat: Add comprehensive JWT authentication with... (#123)' (62 chars)"
   - Decision: **Reject** - The example is intentionally simplified to show the concept. Breaking down every arithmetic step would make it harder to scan.

### Low Priority

4. **Redundant phrasing in rules**
   - Description: Rule 5 states "Issue number is ALWAYS appended automatically" and rule 6 repeats length requirement from rule 5. Some consolidation could improve readability.
   - Suggestion: Consolidate rules 5-6: "5. Issue number (extracted from branch name) is ALWAYS appended automatically. Total length MUST be under 70 characters—truncate description with '...' if needed."
   - Decision: **Implement Now** - Valid concern. Consolidated by simplifying rule 5 to reference the detailed "Issue Number Handling" section, reducing duplication.

5. **Examples could show more edge cases**
   - Description: Current examples show straightforward cases. Adding a truncation example or multi-commit example would reinforce understanding.
   - Suggestion: Add to examples: "- 'feat: Implement comprehensive user authentication system with... (#1234)' (70 chars, truncated)"
   - Decision: **Defer** - Examples currently show the normal/expected case. Edge cases are documented in respective sections.

## Positive Aspects

- **Excellent structure**: The progression from rules → process → when-to-use sections creates a clear mental model
- **Concrete examples**: Multiple examples in different contexts (rules section, HEREDOC, display result) reinforce the format
- **Explicit automation**: Clear statement that issue number is automatically extracted and appended removes ambiguity
- **Process breakdown**: 4-step title generation process provides actionable steps for agents
- **Edge case coverage**: "When to Analyze Diffs" section addresses non-obvious scenarios (generic commit messages)
- **Length constraint handling**: Explicit truncation logic addresses a common failure mode
- **Consistency**: Examples.md update ensures documentation aligns with workflow instructions

## Recommendations

1. **Future enhancement**: Consider adding a validation step after title generation to verify format compliance (length check, issue number presence, type prefix validity)

2. **Process clarity**: Consider adding a decision tree diagram or flowchart for "when to use commit message vs analyze diffs" to visual learners (could be in examples.md)

3. **Error handling**: Add a troubleshooting section for common title generation failures (no commits, empty diffs, branch name parsing errors)

4. **Template consistency**: Ensure the HEREDOC template in step 2.6 also reflects any title format changes (currently correct, but good to note for future updates)

5. **Testing guidance**: Consider adding a note about how to verify generated titles meet all requirements before creating PR

## Files Reviewed

- `.claude/skills/pr/workflows/create.md` (Workflow/Prompt)
- `.claude/skills/pr/assets/examples.md` (Documentation)
