# Mapping Verification Workflow

Verify the accuracy of classification in the generated mapping by reading actual RST content.

**IMPORTANT**: Follow ALL steps in this workflow file exactly as written. Do not skip steps or use summary descriptions from SKILL.md or other files. Read and execute each step according to the detailed instructions provided here.

**IMPORTANT**: Run this workflow in a **separate session** from the generation workflow. This prevents context bias where the same path-based rules used in generation would blind the verification.

## Input

**Version**: Nablarch version number (e.g., `6` for v6, `5` for v5)

## Progress Checklist Template

```
## nabledge-creator verify-mapping {version} - Progress

□ Step VM1: Read Input Files
□ Step VM2: Verify Classification (All Files)
□ Step VM3: Categorize Issues
□ Step VM4: Document Verification Results

**Started:** [timestamp]
**Status:** Not started
```

## Workflow Steps

### Step VM1: Read Input Files

Read the following files:

```
.claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md   # Verification checklist
.claude/skills/nabledge-creator/output/mapping-v{version}.md             # Generated mapping
.claude/skills/nabledge-creator/references/classification.md              # Classification rules
```

The checklist contains all rows from the mapping that require content verification.

### Step VM2: Verify Classification and Target Paths (Batch Processing with Task Tool)

**Batch Processing Strategy**: Use Task tool to process files in category-based batches to avoid context overflow.

#### Step VM2.1: Group Files by Category

Read mapping file and group by `Type / Category`:

```bash
grep "^|" .claude/skills/nabledge-creator/output/mapping-v{version}.md | tail -n +3 | \
  awk -F'|' '{print $5 "/" $6}' | sed 's/^ *//;s/ *$//' | sort | uniq -c
```

Create batches (same as mapping Step 2):
- Categories with >60 files: Split into 2 batches
- Categories with ≤60 files: 1 batch per category
- Save to `.tmp/nabledge-creator/verify-batches-v{version}.json`

#### Step VM2.2: Launch Task Agents (Parallel)

For each batch, launch a Task agent in parallel:

```
Task (parallel × N batches)
  subagent_type: "general-purpose"
  description: "Verify mapping: {category} batch {n}"
  prompt: "You are verifying mapping classification for Nablarch v{version} documentation.

## Your Assignment

**Batch ID**: {batch_id}
**Category**: {type}/{category}
**Files**: {count} files

## Input Files

Read these files first:
1. Mapping file: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`
2. Classification rules: `.claude/skills/nabledge-creator/references/classification.md`
3. Content judgement rules: `.claude/skills/nabledge-creator/references/content-judgement.md`

Extract your batch's file list from the mapping file.

## Your Task

For each file in your batch:

### 1. Read RST Source

- Read first 50 lines from `.lw/nab-official/v{version}/` (Source Path)
- If insufficient, read up to 200 lines or until main content section
- If file contains `toctree`, read referenced files
- Check parent directories for `:ref:` and `toctree` references

### 2. Verify Type and Category

- Check if content matches assigned Type and Category ID
- Determine which rule in classification.md produced this classification
- Confirm rule matches actual content

### 3. Verify Processing Pattern (Critical)

**PP MUST be verified by reading content**

Apply rules from content-judgement.md. Look for indicators in:
- **Title**: Does it mention specific processing pattern?
- **First paragraph**: What does this file describe?
- **Code examples**: What APIs are used?
- **Section headers**: What scenarios are covered?

**Common patterns**:
- testing-framework: Title mentions \"バッチ\", \"RESTful\", \"Messaging\"
- toolbox: Tool targets specific pattern (JSP → web-application)
- libraries: Title includes \"用\" suffix (e.g., \"RESTful Web Service用\")
- handlers: Content indicates pattern usage

### 4. Verify Target Path

- Target Path starts with Type (e.g., `component/`, `processing-pattern/`)
- Filename correctly converts Source Path (`_` → `-`, `.rst` → `.json`)
- For component category, subdirectories are preserved

### 5. Record Result

For each file, record:
```
File: {source_path}
Type/Category: {type}/{category} - ✓ / ✗ {correct if wrong}
PP: {pp_value} - ✓ / ✗ {correct if wrong}
Target Path: {path} - ✓ / ✗ {issue if wrong}
Notes: {reasoning for any ✗}
```

## Output

After completing all files in your batch:

**Report completion**:
```
Batch {batch_id} complete:
- Files verified: {count}/{count}
- Classification correct: {correct_count}
- Classification errors: {error_count}
- PP errors: {pp_error_count}
- Path errors: {path_error_count}
```

**Update progress file**:
Write to `.tmp/nabledge-creator/verify-progress-v{version}.json`:
```json
{
  \"batch_id\": \"{batch_id}\",
  \"status\": \"complete\",
  \"verified\": {count},
  \"errors\": {error_count},
  \"details\": [{\"file\": \"path\", \"issue\": \"description\"}]
}
```

## Important Notes

- Verify ALL files in your batch
- Read actual RST content - do NOT guess from path
- PP cannot be determined by path alone - MUST read content
- Document all ✗ marks with reasoning
"
  run_in_background: false
```

Launch all batches in parallel (use multiple Task calls in one message).

#### Step VM2.3: Verify Completion

After all Task agents complete:

```bash
# Count total files
TOTAL=$(grep -v "^#" .claude/skills/nabledge-creator/output/mapping-v{version}.md | grep "^|" | tail -n +3 | wc -l)

# Sum verified from progress files
VERIFIED=$(jq -s 'map(.verified) | add' .tmp/nabledge-creator/verify-progress-v{version}.json)

# Count errors
ERRORS=$(jq -s 'map(.errors) | add' .tmp/nabledge-creator/verify-progress-v{version}.json)

echo "Total files: $TOTAL"
echo "Files verified: $VERIFIED"
echo "Errors found: $ERRORS"
```

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Total files in mapping | [count from mapping file] | [count] | ✓ |
| Files verified | [total files] | [sum from progress files] | ✓/✗ |
| Task agents launched | [batches count] | [count] | ✓ |
| All batches complete | Yes | [check progress files] | ✓/✗ |
| Classification errors | 0 or documented | [error count] | ✓/✗ |

**How to measure:**
- Total files: Row count in mapping-v{version}.md (minus headers)
- Files verified: Sum of "verified" from all progress files
- All batches complete: All progress files have "status": "complete"
- Errors: Sum of "errors" from all progress files

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

Save the updated checklist to `.claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md`.

## Verification Complete

When all checklist items are marked ✓, the mapping verification is complete. The mapping file `.claude/skills/nabledge-creator/output/mapping-v{version}.md` is ready for use in knowledge file generation.

## Why Separate Session?

The generation session uses path patterns to classify files. If we verify in the same session, we unconsciously apply the same patterns and miss errors. By reading RST content in a fresh session, we catch cases where path patterns led to wrong classifications.
