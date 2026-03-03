# Expert Review: Prompt Engineer

**Date**: 2026-03-03
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The changes successfully fix critical bugs and improve agent behavior by adding expected sections guidance. The prompts are clear and well-structured, but there are opportunities to strengthen validation instructions and clarify edge case handling.

## Key Issues

### High Priority

None identified. The changes correctly address the root causes and improve prompt quality.

### Medium Priority

1. **Expected Sections: Ambiguity in "not empty" check**
   - **Description**: The instruction "If this list is not empty, you MUST generate ALL sections listed above" relies on the agent interpreting "not empty" correctly. The template variable `{EXPECTED_SECTIONS}` could be a blank line, whitespace, or literally empty, which might confuse the agent.
   - **Suggestion**: Add explicit formatting guidance:
     ```markdown
     ## Expected Sections (if this file was split)

     {EXPECTED_SECTIONS}

     **If sections are listed above**: Use that list. You MUST generate ALL sections from that list — do not skip any.

     **If no sections are listed above** (empty or blank): Scan the source yourself in Step 2.
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: Current wording is likely sufficient for Claude to interpret correctly. Can be refined if field testing reveals confusion. The improvement would be incremental rather than critical.

2. **Missing validation for section count mismatch**
   - **Description**: generate.md instructs agents to use expected sections but doesn't include a final validation step to confirm the count matches. If the agent mistakenly skips a section, there's no self-check to catch it.
   - **Suggestion**: Add to "Final self-checks before output" section:
     ```markdown
     - [ ] If Expected Sections was provided, section count equals expected count
     ```
   - **Decision**: Implement Now
   - **Reasoning**: This is a straightforward addition that directly addresses the original bug (missing sections). Adds defensive validation with minimal cost.

3. **content_check.md: No explicit instruction about expected line count**
   - **Description**: While the fix correctly removes extra content, the prompt doesn't include guidance for validators to check for unexpected content duplication or file size anomalies. Future copy-paste errors could go undetected.
   - **Suggestion**: Add a validation check:
     ```markdown
     ### V5: File Structure (severity: minor)

     - Check for duplicate prompt sections or repeated content blocks
     - Verify prompt structure matches expected format (intro, checklist, output)
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: This is more about prompt file hygiene than content validation. The current checklist is comprehensive for knowledge file validation. Adding structural validation would be valuable but is not urgent for the current bug fix scope.

### Low Priority

1. **Step 2 instruction redundancy**
   - **Description**: The instructions repeat "you MUST generate ALL sections" in both the Expected Sections block and Step 2. While emphasis is good, it creates slight redundancy.
   - **Suggestion**: Streamline by keeping the imperative in Step 2 and making the Expected Sections block more descriptive:
     ```markdown
     ## Expected Sections (if this file was split)

     {EXPECTED_SECTIONS}

     The above list shows sections detected by the classification tool. Use this list in Step 2 if provided.
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: Redundancy serves as emphasis here and reduces risk of the agent missing the instruction. Streamlining is a polish improvement, not a functional necessity.

2. **Example formatting for Expected Sections template**
   - **Description**: The prompt doesn't show agents what `{EXPECTED_SECTIONS}` will look like (numbered list? bullet points? plain text?). Including an example could improve clarity.
   - **Suggestion**: Add a comment showing expected format:
     ```markdown
     {EXPECTED_SECTIONS}
     <!-- Example format:
     1. overview
     2. setup-guide
     3. advanced-features
     -->
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: The actual format depends on step2_classify.py implementation. Adding examples requires coordination between code and prompt. Current implementation is sufficient for agents to parse the list.

## Positive Aspects

- **Root cause addressed**: The fix for content_check.md directly removes the problematic content that caused validation failures. Clean and precise.
- **Clear problem statement**: The Expected Sections feature in generate.md explains WHY the list is provided (context: classification tool detected 65 sections, agent previously missed some).
- **Explicit fallback logic**: "If empty, scan the source yourself" provides clear fallback behavior, maintaining backward compatibility.
- **Preserves existing structure**: The change integrates seamlessly into the existing Work Steps framework without disrupting other sections.
- **Strong imperative language**: "MUST generate ALL sections" leaves no room for misinterpretation about the requirement.
- **Self-documentation**: The trace log structure in Step 2 ensures decisions are recorded for debugging.

## Recommendations

1. **Add section count validation**: Implement the suggested self-check to verify expected section count matches generated count (Medium Priority #2). This provides defense-in-depth against section skipping bugs.

2. **Field testing with edge cases**: Test the Expected Sections feature with:
   - Empty list (ensure fallback works)
   - Single section (ensure no index confusion)
   - Very large section lists (65+ sections, like tag_reference.rst)
   - Mismatched section names (classification tool uses different naming than source headings)

3. **Monitor for section name mismatches**: If step2_classify.py generates section IDs like "date-time-local-tag" but the agent interprets the heading as "datetime-local-tag", there could be mismatches. Consider adding fuzzy matching guidance or exact ID enforcement in the prompt.

4. **Document template variable format**: Add a comment in step2_generate.py showing the exact format of {EXPECTED_SECTIONS} output (helps future prompt maintainers understand dependencies).

5. **Consider adding trace log for Expected Sections usage**: To help debug future issues, consider adding a trace field like:
   ```json
   "trace": {
     "expected_sections_provided": true,
     "expected_sections_count": 65,
     "generated_sections_count": 65
   }
   ```

## Files Reviewed

- tools/knowledge-creator/prompts/content_check.md (validation prompt)
- tools/knowledge-creator/prompts/generate.md (generation prompt)
