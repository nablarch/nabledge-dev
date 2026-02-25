# Mapping Verification Workflow

Verify the accuracy of classification in the generated mapping by reading actual RST content.

**IMPORTANT**: Run this workflow in a **separate session** from the generation workflow. This prevents context bias where the same path-based rules used in generation would blind the verification.

## Invocation

```
nabledge-creator verify-mapping-6
```

## Workflow Steps

### Step VM1: Read Input Files

Read the following files:

```
.claude/skills/nabledge-creator/output/mapping-v6.checklist.md   # Verification checklist
.claude/skills/nabledge-creator/output/mapping-v6.md             # Generated mapping
.claude/skills/nabledge-creator/references/classification.md     # Classification rules
```

The checklist contains all rows from the mapping that require content verification.

### Step VM2: Verify Classification (All 291 Files)

For each row in the mapping file (all 291 files):

1. **Read RST source**:
   - Read the first 50 lines of the RST file specified in Source Path
   - If these lines don't contain sufficient information to verify classification (e.g., file is mostly boilerplate or toctree directives), read up to 200 lines or until you find the main content section
   - If the file contains `toctree` directives, read those referenced files as well
   - Read any files that reference this file (check `:ref:` and `toctree` in parent directories)

2. **Verify Type and Category**:
   - Check if the content matches the assigned Type and Category ID
   - Determine which rule in `.claude/skills/nabledge-creator/references/classification.md` produced this classification
   - Confirm the rule matches the actual content

3. **Verify Processing Pattern** (Critical):
   - **Processing Pattern MUST be verified by reading content**
   - Apply rules from `.claude/skills/nabledge-creator/references/content-judgement.md`
   - Look for indicators in:
     - Title (does it mention a specific processing pattern?)
     - First paragraph (what does this file describe?)
     - Code examples (what APIs are used?)
     - Section headers (what scenarios are covered?)
   - Confirm PP assignment matches content indicators
   - **Common patterns to check**:
     - development-tools/testing-framework: Title mentions "バッチ", "RESTful", "Messaging", etc.
     - development-tools/toolbox: Tool targets specific pattern (e.g., JSP → web-application)
     - component/libraries: Title includes "用" suffix indicating pattern-specific (e.g., "RESTful Web Service用")
     - component/handlers: Path suggests pattern (e.g., `/rest/` → restful-web-service)

4. **Record result**:
   - If classification is correct: Mark ✓
   - If classification is incorrect: Mark ✗ and record the correct classification
   - For PP errors, note what indicators were found vs what was assigned

**Do NOT skip this step**. Reading the actual content is the only way to catch classification errors, especially for Processing Pattern which cannot be determined by path alone.

**Verification scope**: All 291 files must be verified. Use Task tool with batch processing if needed to handle large volume efficiently.

### Step VM3: Verify Target Paths (All 291 Files)

For each row in the mapping file (all 291 files):

1. **Verify path structure**:
   - Target Path starts with Type (e.g., `component/`, `processing-pattern/`)
   - Filename correctly converts Source Path filename (`_` → `-`, `.rst` → `.md`)
   - For component category, subdirectories are preserved

2. **Record result**:
   - If path is correct: Mark ✓
   - If path has errors: Mark ✗ and note the issue

### Step VM4: Apply Corrections

If ANY row is marked ✗:

1. Document the corrections needed in the checklist file (note the correct classification and reasoning)
2. **Exit the verification session** (this is critical - don't continue in same session)
3. **In a new generation session**, apply corrections to `.claude/skills/nabledge-creator/references/classification.md` and `generate-mapping.py`
4. Re-run the generation workflow from Step 1
5. **Start a fresh verification session** after regeneration completes

Do NOT proceed with incorrect classifications. Session separation ensures that verification remains unbiased by generation logic.

### Step VM5: Update Checklist

Update the checklist with verification results:

- Mark each row with ✓ or ✗
- Add notes explaining any ✗ marks
- If all rows are ✓, mark the verification as complete

Save the updated checklist to `.claude/skills/nabledge-creator/output/mapping-v6.checklist.md`.

## Verification Complete

When all checklist items are marked ✓, the mapping verification is complete. The mapping file `.claude/skills/nabledge-creator/output/mapping-v6.md` is ready for use in knowledge file generation.

## Why Separate Session?

The generation session uses path patterns to classify files. If we verify in the same session, we unconsciously apply the same patterns and miss errors. By reading RST content in a fresh session, we catch cases where path patterns led to wrong classifications.
