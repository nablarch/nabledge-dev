# Expert Review: Prompt Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured workflow improvements that clearly automate deterministic tasks and reduce LLM workload. Instructions are generally clear with good technical detail, though some areas need clarification around error handling, validation, and the relationship between steps.

## Key Issues

### High Priority

1. **Missing script error handling guidance**
   - Description: Steps 3.2 and 3.3 introduce Bash scripts but provide no guidance on what the agent should do if scripts fail (missing dependencies, permission errors, script bugs, etc.). This could leave the agent stuck or proceeding with incomplete data.
   - Suggestion: Add error handling instructions:
     ```markdown
     **If script fails**:
     - Read script output to understand the error
     - Check if required dependencies are installed
     - Verify input parameters match expected format
     - If script has a bug, report to user and fall back to manual placeholder filling
     ```

2. **Unclear validation requirements between steps**
   - Description: Step 3.2 pre-fills 8 placeholders and Step 3.3 generates diagram skeletons, but there's no instruction to validate these outputs before proceeding to Step 3.4. Agent might refine malformed skeletons or work with incorrect pre-filled data.
   - Suggestion: Add validation checkpoint after Steps 3.2 and 3.3:
     ```markdown
     **Before proceeding to Step 3.4**:
     - Verify all 8 deterministic placeholders are filled (not empty or error messages)
     - Confirm diagram skeletons contain valid Mermaid syntax
     - Check that source_files_links and knowledge_base_links arrays are properly formatted
     ```

### Medium Priority

1. **Script parameter documentation could be more discoverable**
   - Description: Step 3.2 embeds parameter explanations in prose format. If an agent needs to reference parameter requirements later, they must re-read the entire section.
   - Suggestion: Format parameters as a reference table:
     ```markdown
     | Parameter | Description | Example |
     |-----------|-------------|---------|
     | target_name | Name of target (class/package) | `DateTimeConverter` |
     | target_description | Brief description | `Converts between Date and String formats` |
     | ... | ... | ... |
     ```

2. **Ambiguous "refinement" expectations in Step 3.4**
   - Description: Instructions say "refine skeletons instead of generating from scratch" but don't specify what level of refinement is expected. Should agents add all details, or just fix obvious errors?
   - Suggestion: Clarify refinement scope:
     ```markdown
     **Refinement expectations**:
     - Add missing entities/methods/participants based on code analysis
     - Correct relationship directions and multiplicities
     - Add descriptive labels and annotations
     - Ensure diagram accurately represents actual code structure
     - Do not change overall structure unless factually incorrect
     ```

3. **Step 3.5 placeholder list could be clearer**
   - Description: States "8 placeholders need to be filled by LLM (down from 16)" but doesn't explicitly list which 8. Agent must infer from Step 3.2's list.
   - Suggestion: Add explicit list in Step 3.5:
     ```markdown
     **Placeholders to fill (8)**:
     1. `{{key_points}}` - Core functionality highlights
     2. `{{architecture_overview}}` - High-level architecture description
     3. `{{detailed_explanation}}` - In-depth technical details
     4. `{{usage_examples}}` - Code examples
     5. `{{error_handling}}` - Error handling patterns
     6. `{{testing_strategy}}` - Testing approach
     7. `{{related_components}}` - Dependencies and relationships
     8. `{{notes}}` - Additional notes and considerations
     ```

### Low Priority

1. **Time savings claim lacks context**
   - Description: States "expected to significantly reduce processing time" but doesn't quantify or explain why. Would be more persuasive with rough estimates.
   - Suggestion: Add concrete estimate:
     ```markdown
     **Expected time savings**: ~30-40% reduction in processing time by eliminating redundant LLM calls for deterministic data (metadata, file paths, timestamps) and providing structured starting points for diagrams.
     ```

2. **Missing troubleshooting guidance for common issues**
   - Description: No guidance for common problems like missing modules, empty source files, or incorrect knowledge base paths.
   - Suggestion: Add troubleshooting section after Step 3.3:
     ```markdown
     **Common Issues**:
     - Empty `source_files_links`: Ensure target files exist in analyzed codebase
     - Missing knowledge base files: Check `.claude/skills/nabledge-6/knowledge/` directory
     - Invalid Mermaid syntax: Verify class/sequence diagram type matches code structure
     ```

## Positive Aspects

- **Clear step decomposition**: Breaking Step 3 into 3.2, 3.3, 3.4, 3.5 creates logical, sequential stages that are easy to follow
- **Excellent automation rationale**: Clearly explains why scripts handle deterministic data (metadata, timestamps, file paths) vs. why LLM handles semantic content
- **Good tool specification**: Explicitly lists required tools (Bash, Read, Edit, Write) upfront in each step
- **Practical script documentation**: Step 3.2 and 3.3 include parameter explanations and expected outputs, not just command syntax
- **Maintains workflow continuity**: Changes integrate smoothly without disrupting Steps 1, 2, 4, 5 (renumbering is clean)
- **Reduces cognitive load**: Pre-filled templates and diagram skeletons give agents concrete starting points rather than blank pages

## Recommendations

1. **Add validation checkpoints**: Insert explicit validation steps after automated script execution to catch errors early
2. **Create script troubleshooting appendix**: Document common script failures and recovery procedures in a dedicated section
3. **Consider adding examples**: Include a small before/after example showing a skeleton diagram and its refined version
4. **Quantify improvements**: Add metrics (time saved, placeholder reduction) to help users understand workflow efficiency gains
5. **Future enhancement**: Consider adding a Step 3.6 for automated diagram validation (syntax checking, entity name verification) to catch issues before manual review

## Files Reviewed

- /home/tie303177/work/nabledge/work7/.claude/skills/nabledge-6/workflows/code-analysis.md (workflow)
