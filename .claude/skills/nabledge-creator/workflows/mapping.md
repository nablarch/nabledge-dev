# Mapping Generation Workflow

Generate documentation mapping from Nablarch official documentation to nabledge knowledge file structure.

**IMPORTANT**: Follow ALL steps in this workflow file exactly as written. Do not skip steps or use summary descriptions from SKILL.md or other files. Read and execute each step according to the detailed instructions provided here.

## Input

Skill invocation format: `nabledge-creator mapping {version}`

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

Extract version number from skill arguments. Throughout this workflow, use `v{version}` format for paths and commands (e.g., `v6`, `v5`).

## Progress Checklist Template

```
## nabledge-creator mapping {version} - Progress

□ Step 1: Generate Base Mapping (Path-based)
□ Step 2: Assign Processing Patterns (Content-based)
□ Step 3: Validate Mapping
□ Step 4: Export to Excel
□ Step 5: Resolve Review Items (if needed)
□ Step 6: Generate Verification Checklist

**Started:** [timestamp]
**Status:** Not started
```

## Workflow Steps

### Step 1: Generate Base Mapping (Path-based Classification Only)

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping.py "v{version}"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`

**What this step does**:
- Classifies Type and Category based on path patterns only
- Does NOT assign Processing Pattern (all PP fields are empty initially)
- Reports review items for files where path-based classification is uncertain

**Exit Code Handling**:

Check the script's exit code to determine next steps:

- **Exit 0**: Success - No review items found. Proceed to Step 2 (Assign Processing Patterns)
- **Exit 1**: Review items exist - Review items printed to stdout in JSON format. Skip to Step 5 (Resolve Review Items) before proceeding to Step 2
- **Exit 2**: Script error - Fix script issues (invalid input, file not found, etc.) and re-run Step 1

Do not proceed to Step 2 until all review items from exit code 1 are resolved.

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Exit code | 0 or 1 (not 2) | [code] | ✓/✗ |
| Output file exists | mapping-v{version}.md | [ls check] | ✓/✗ |
| Files enumerated | >0 | [from "Found N files" in output] | ✓ |
| Files mapped | [enumerated count] | [grep -c "^|" mapping file minus headers] | ✓/✗ |
| Review items | 0 or documented | [from output] | ✓/✗ |

**How to measure:**
- Exit code: Script return value
- File counts: Parse "Found 329 files", "Completed: 329 files mapped" from output
- Row count: `grep "^|" mapping-v{version}.md | wc -l` then subtract 2 (header rows)
- Review items: Look for "Review items: N" in output, or check exit code 1

**Important:** If exit code is 1, go to Step 5 before proceeding to Step 2.

### Step 2: Assign Processing Patterns (Content-based with Task Tool)

**Critical**: This step reads file content to determine Processing Pattern for ALL files.

**Processing Pattern MUST be determined by reading content, NOT by path patterns.**

**Batch Processing Strategy**: Use Task tool to process files in category-based batches to avoid context overflow.

#### Step 2.1: Group Files by Category

Read the mapping file and group files by `Type / Category`:

```bash
grep "^|" .claude/skills/nabledge-creator/output/mapping-v{version}.md | tail -n +3 | \
  awk -F'|' '{print $5 "/" $6}' | sed 's/^ *//;s/ *$//' | sort | uniq -c
```

Create batches:
- Categories with >60 files: Split into 2 batches (~30 files each)
- Categories with ≤60 files: 1 batch per category
- Save batch definitions to `.tmp/nabledge-creator/pp-batches-v{version}.json`

#### Step 2.2: Launch Task Agents (Parallel)

For each batch, launch a Task agent in parallel:

```
Task (parallel × N batches)
  subagent_type: "general-purpose"
  description: "Assign PP: {category} batch {n}"
  prompt: "You are assigning Processing Patterns (PP) for Nablarch v{version} documentation.

## Your Assignment

**Batch ID**: {batch_id}
**Category**: {type}/{category}
**Files**: {count} files

## Input

Read these files:
1. Mapping file: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`
2. Content rules: `.claude/skills/nabledge-creator/references/content-judgement.md`

Extract your batch's file list from the mapping file (rows where Type={type} AND Category={category}).

## Your Task

For each file in your batch:

1. **Read RST content** (first 50-100 lines from `.lw/nab-official/v{version}/`)
   - Read both English (en/) and Japanese (ja/) versions if available

2. **Apply PP determination rules** from content-judgement.md:
   - Look at title: Does it mention specific processing pattern?
   - Look at first paragraph: What does this file describe?
   - Look at code examples: What APIs/classes are used?
   - Look at section headers: What scenarios are covered?

3. **Assign PP**:
   - If pattern-specific → Assign corresponding PP (e.g., 'web-application', 'restful-web-service', 'nablarch-batch', etc.)
   - If common/general-purpose → Leave PP empty ('')
   - Confidence: Document reasoning for each assignment

4. **Update mapping file**:
   - Modify the PP column for your batch's rows
   - Use Edit tool to update `.claude/skills/nabledge-creator/output/mapping-v{version}.md`

## PP Values

Valid PP values (or empty string for common/general):
- jakarta-batch
- nablarch-batch
- web-application
- restful-web-service
- http-messaging
- mom-messaging
- db-messaging

## Output

After completing all files in your batch:

**Report completion**:
```
Batch {batch_id} complete:
- Files processed: {count}/{count}
- PP assigned: {assigned_count}
- PP empty (common): {empty_count}
```

**Update progress file**:
Write to `.tmp/nabledge-creator/pp-progress-v{version}.json`:
```json
{
  \"batch_id\": \"{batch_id}\",
  \"status\": \"complete\",
  \"processed\": {count},
  \"pp_assigned\": {assigned_count},
  \"pp_empty\": {empty_count}
}
```

## Important Notes

- Process ALL files in your batch
- Read actual RST content - do NOT guess from path
- When in doubt, leave PP empty (common/general-purpose)
- Document reasoning for pattern-specific assignments
"
  run_in_background: false
```

Launch all batches in parallel (use multiple Task calls in one message).

#### Step 2.3: Verify Completion

After all Task agents complete:

```bash
# Count total files
TOTAL=$(grep -v "^#" .claude/skills/nabledge-creator/output/mapping-v{version}.md | grep "^|" | tail -n +3 | wc -l)

# Count files with PP assigned
ASSIGNED=$(grep -v "^#" .claude/skills/nabledge-creator/output/mapping-v{version}.md | grep "^|" | tail -n +3 | awk -F'|' '{print $8}' | sed 's/^ *//;s/ *$//' | grep -v "^$" | wc -l)

echo "Total files: $TOTAL"
echo "Files with PP: $ASSIGNED"
echo "Files without PP (common): $((TOTAL - ASSIGNED))"
```

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Files in mapping | [from Step 1] | [count] | ✓ |
| Files processed | [from Step 1] | [all files] | ✓/✗ |
| Task agents launched | [batches count] | [count] | ✓ |
| All batches complete | Yes | [check progress files] | ✓/✗ |

**How to measure:**
- Files in mapping: Row count from Step 1
- Files processed: Sum of "processed" from all progress files
- All batches complete: All progress files have "status": "complete"

### Step 3: Validate Mapping

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/validate-mapping.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md"
```

**Expected result**: All checks pass

If any check fails:
1. Read the error message carefully
2. Identify which rule in `generate-mapping.py` needs correction
3. Fix the rule
4. Return to Step 1

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Exit code | 0 or 1 (warnings OK) | [code] | ✓/✗ |
| Structure check | PASS | [from output] | ✓/✗ |
| Taxonomy check | PASS | [from output] | ✓/✗ |
| Source files check | PASS | [from output] | ✓/✗ |
| Target paths check | PASS | [from output] | ✓/✗ |
| URL format check | PASS | [from output] | ✓/✗ |
| Consistency check | PASS | [from output] | ✓/✗ |

**How to measure:**
- Parse validation output for each check result
- Exit code 1 with warnings is acceptable if documented
- Any FAIL status requires fixing

### Step 4: Export to Excel

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/export-excel.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v${version}.xlsx`

This Excel file is for human review and is not used in automated workflows.

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Output file exists | mapping-v{version}.xlsx | [ls check] | ✓/✗ |
| Row count | [from mapping MD] | [from script output] | ✓/✗ |

### Step 5: Resolve Review Items

Execute this step ONLY if Step 1 reported review items (exit code 1).

Review items are files where path-based classification was insufficient. For each review item:

1. **Read context**:
   - Read the target RST file
   - Read other files in the same directory
   - Check `:ref:` references and `toctree` directives that point to or from this file

2. **Make decision**:
   - If you can determine the correct classification, add a rule to `.claude/skills/nabledge-creator/references/classification.md`
   - Update `generate-mapping.py` to implement the new rule
   - Return to Step 1

3. **If uncertain**:
   - Report to human with detailed reasoning why classification is ambiguous
   - Include file path, context examined, and conflicting indicators

Do NOT guess. If the classification is genuinely ambiguous, human judgment is required.

#### How to Add New Rules

When adding new classification rules, update both files to ensure synchronization:

1. **Update generate-mapping.py**:
   - Add path-based rule to the `classify_by_path()` function in the appropriate section
   - Use `if path.startswith('...')` pattern for directory-based rules
   - Use `if 'keyword' in path` for keyword-based rules
   - Example: `if path_for_matching.startswith('application_framework/libraries/'):`

2. **Update references/classification.md**:
   - Add corresponding entry using the format specified in that file
   - Include rationale explaining why this path pattern maps to this classification
   - Include examples of files matching this rule

3. **Ensure synchronization**:
   - Both files must stay synchronized to maintain reproducibility
   - Test by running generate-mapping.py and verifying new classifications appear correctly
   - Run validation to confirm rules work as expected

### Step 6: Generate Verification Checklist

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping-checklist.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md" --source-dir ".lw/nab-official/v{version}/" --output ".claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v${version}.checklist.md`

This checklist is used in the verification session (`verify-mapping` workflow) to confirm classification accuracy (including Processing Pattern) by reading RST content.

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Output file exists | mapping-v{version}.checklist.md | [ls check] | ✓/✗ |
| Classification checks | [mapping row count] | [from script output] | ✓/✗ |
| Target path checks | [mapping row count] | [from script output] | ✓/✗ |

## Generation Session Complete

Hand off the checklist to the verification session. The verification workflow (`verify-mapping`) runs in a separate session to avoid context bias.

## Input Directories

```
.lw/nab-official/v{version}/nablarch-document/en/
.lw/nab-official/v{version}/nablarch-document/ja/
.lw/nab-official/v{version}/nablarch-system-development-guide/
```

## Output Files

```
.claude/skills/nabledge-creator/output/mapping-v{version}.md          # Markdown table
.claude/skills/nabledge-creator/output/mapping-v{version}.xlsx        # Excel table (human review)
.claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md # Verification checklist
```

## Reference Files

You may need to read these files during Step 4 (review item resolution):

- `.claude/skills/nabledge-creator/references/classification.md` - Path pattern classification rules
- `.claude/skills/nabledge-creator/references/target-path.md` - Path conversion rules
- `.claude/skills/nabledge-creator/references/content-judgement.md` - Content-based judgement rules
