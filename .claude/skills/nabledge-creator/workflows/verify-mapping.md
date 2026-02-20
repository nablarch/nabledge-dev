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
references/mapping/mapping-v6.checklist.md   # Verification checklist
references/mapping/mapping-v6.md             # Generated mapping
references/classification.md                 # Classification rules
```

The checklist contains sampled rows from the mapping that require content verification.

### Step VM2: Verify Classification (Sampled Rows)

For each row in the checklist's "Classification Check" section:

1. **Read RST source**:
   - Read the first 50 lines of the RST file specified in Source Path
   - If the file contains `toctree` directives, read those referenced files as well
   - Read any files that reference this file (check `:ref:` and `toctree` in parent directories)

2. **Verify classification**:
   - Check if the content matches the assigned Type, Category ID, and Processing Pattern
   - Determine which rule in `references/classification.md` produced this classification
   - Confirm the rule matches the actual content

3. **Record result**:
   - If classification is correct: Mark ✓
   - If classification is incorrect: Mark ✗ and record the correct classification

**Do NOT skip this step**. Reading the actual content is the only way to catch path-based classification errors.

### Step VM3: Verify Target Paths (Sampled Rows)

For each row in the checklist's "Target Path Check" section:

1. **Verify path structure**:
   - Target Path starts with Type (e.g., `component/`, `processing-pattern/`)
   - Filename correctly converts Source Path filename (`_` → `-`, `.rst` → `.md`)
   - For component category, subdirectories are preserved

2. **Record result**:
   - If path is correct: Mark ✓
   - If path has errors: Mark ✗ and note the issue

### Step VM4: Apply Corrections

If ANY row is marked ✗:

1. Identify the incorrect rule in `references/classification.md`
2. Correct the rule
3. Return to the generation workflow and re-run from Step 1

Do NOT proceed with incorrect classifications.

### Step VM5: Update Checklist

Update the checklist with verification results:

- Mark each row with ✓ or ✗
- Add notes explaining any ✗ marks
- If all rows are ✓, mark the verification as complete

Save the updated checklist to `references/mapping/mapping-v6.checklist.md`.

## Verification Complete

When all checklist items are marked ✓, the mapping verification is complete. The mapping file `references/mapping/mapping-v6.md` is ready for use in knowledge file generation.

## Why Separate Session?

The generation session uses path patterns to classify files. If we verify in the same session, we unconsciously apply the same patterns and miss errors. By reading RST content in a fresh session, we catch cases where path patterns led to wrong classifications.
