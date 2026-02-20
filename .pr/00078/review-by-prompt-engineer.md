# Expert Review: Prompt Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 3 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured workflow documentation with clear step-by-step instructions and strong separation of concerns. The workflows demonstrate good prompt engineering principles with explicit agent behavior guidance, error handling, and decision-making protocols. Minor improvements needed for ambiguity resolution and example quality.

## Key Issues

### High Priority

1. **Ambiguous Instruction: "Read the first 50 lines"**
   - **Location**: `verify-mapping.md`, Step VM2
   - **Description**: The instruction says "Read the first 50 lines of the RST file" but doesn't specify what to do if critical classification information appears after line 50.
   - **Suggestion**: Add explicit guidance: "Read the first 50 lines of the RST file. If these lines don't contain sufficient information to verify classification (e.g., file is mostly boilerplate or toctree), read up to 200 lines or until you find the main content section."
   - **Decision**: Implement Now
   - **Reasoning**: Agent might fail verification due to arbitrary line limit cutting off relevant content.

2. **Missing Error Recovery Path in Step 4**
   - **Location**: `mapping.md`, Step 4 (Resolve Review Items)
   - **Description**: The workflow says "Update `generate-mapping.py` to implement the new rule" but doesn't specify WHERE in the Python file to add rules or what format they should take.
   - **Suggestion**: Add concrete guidance: "Add the new rule to the appropriate section in `generate-mapping.py` (see existing rules for format). Update the corresponding entry in `references/classification.md` using the format specified in that file. Ensure both files stay synchronized."
   - **Decision**: Implement Now
   - **Reasoning**: Agent may add rules inconsistently or fail to maintain synchronization between files.

### Medium Priority

3. **Incomplete Success Criteria for Step VM4**
   - **Location**: `verify-mapping.md`, Step VM4
   - **Description**: "Return to the generation workflow and re-run from Step 1" is vague about session management. The whole point is separate sessions - does the agent stay in verification session or switch back?
   - **Suggestion**: Clarify: "1. Document the corrections needed in the checklist file. 2. Exit the verification session. 3. In a new generation session, apply the corrections to `references/classification.md` and re-run from Step 1. 4. Start a fresh verification session after regeneration."
   - **Decision**: Implement Now
   - **Reasoning**: Agent might lose the separate-session benefit by trying to fix issues in the same context.

4. **Exit Code Handling Could Be Clearer**
   - **Location**: `mapping.md`, Step 1
   - **Description**: Exit code 1 means "proceed to Step 4" but Step 4 says "Execute this step ONLY if Step 1 reported review items". The conditional logic could be more explicit.
   - **Suggestion**: Restructure to make the branching clearer: "**If exit code is 0**: Proceed to Step 2. **If exit code is 1**: Review items exist. Skip to Step 4 to resolve them before proceeding. **If exit code is 2**: Fix script errors and re-run Step 1."
   - **Decision**: Implement Now
   - **Reasoning**: Agent might execute steps in wrong order or skip necessary validation.

5. **No Example of Review Item Format**
   - **Location**: `mapping.md`, Step 4
   - **Description**: Says "review items will be printed to stdout in JSON format" but doesn't show what this JSON looks like or what fields it contains.
   - **Suggestion**: Add example: "Review items JSON format: `[{\"path\": \"source/path/file.rst\", \"reason\": \"Ambiguous classification due to mixed content\", \"context\": {...}}]`"
   - **Decision**: Defer to Future
   - **Reasoning**: Agent may not correctly parse or interpret review items from script output, but this is lower priority since the format is defined in the script itself.

### Low Priority

6. **Inconsistent Step Numbering Style**
   - **Location**: `verify-mapping.md`, Steps VM1-VM5
   - **Description**: Uses "VM" prefix (VM1, VM2) while `mapping.md` uses plain numbers. While functional, inconsistent styling reduces scannability.
   - **Suggestion**: Either use consistent "Step 1, Step 2" everywhere, or add "Step M1-M5" prefix to mapping.md for symmetry. Current "VM" prefix is helpful for distinguishing verification steps.
   - **Decision**: Defer to Future
   - **Reasoning**: Minor - doesn't affect functionality but could improve navigation.

7. **Missing Rationale for 50-Line Limit**
   - **Location**: `verify-mapping.md`, Step VM2
   - **Description**: Specifies "first 50 lines" without explaining why this limit exists.
   - **Suggestion**: Add brief rationale: "Read the first 50 lines (sufficient for most headers, toctrees, and introductory content)"
   - **Decision**: Defer to Future
   - **Reasoning**: Agent understands the intent better and can make better decisions about when to read more.

## Positive Aspects

- **Excellent Separation of Concerns**: The separate-session verification design is brilliant prompt engineering. It prevents the agent from using cached knowledge of path-based rules when verifying content, creating a genuine second-pass review.

- **Clear Error State Handling**: Exit codes and error conditions are well-defined throughout. The "Do NOT guess" instruction in Step 4 is particularly strong - it prevents hallucination.

- **Structured Decision Points**: Step 4's three-part decision process (Read context → Make decision → If uncertain) guides agent behavior explicitly without ambiguity.

- **Complete Context Provision**: Both workflows list all input files, output files, reference files, and scripts upfront. This gives the agent full situational awareness.

- **Actionable Instructions**: Every step has concrete commands to execute. No vague "analyze the data" instructions.

- **Good Failure Recovery**: The iterative loop (Step 1 → validation fails → fix → return to Step 1) is clearly defined.

- **Purpose-Driven Design**: The "Why Separate Session?" section explains the reasoning, which helps the agent understand the intent behind the structure.

## Recommendations

### Immediate Improvements

1. **Add Examples Section** to both workflows showing:
   - Sample review item JSON output
   - Example of a correct classification rule in `classification.md`
   - Example checklist entry with ✓ and ✗ marks

2. **Create Decision Tree Diagram** in comments or ASCII art showing the flow:
   ```
   Step 1 → exit 0 → Step 2 → Step 3 → Step 5 → Done
         → exit 1 → Step 4 → Step 1 (loop)
         → exit 2 → Fix script → Step 1 (retry)
   ```

3. **Add Validation Step** at the end of Step 4 in `mapping.md`: "After updating rules, verify the change by running `git diff references/classification.md` to confirm the new rule matches your intent."

### Future Enhancements

4. **Consider Adding a "Common Pitfalls" Section** documenting typical misclassifications or errors the agent might encounter. This serves as implicit training data for the agent.

5. **Add Checkpoint Mechanism**: For long verification sessions with many checklist items, add guidance on how to save intermediate state if the session needs to be paused.

6. **Tool Requirements Section**: List prerequisite tools (Python version, required packages) explicitly so agent can verify environment before starting.

## Files Reviewed

- `.claude/skills/nabledge-creator/SKILL.md` (Skill Definition)
- `.claude/skills/nabledge-creator/workflows/mapping.md` (Mapping Generation Workflow)
- `.claude/skills/nabledge-creator/workflows/verify-mapping.md` (Mapping Verification Workflow)
