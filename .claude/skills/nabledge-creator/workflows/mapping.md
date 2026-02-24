# Mapping Generation Workflow

Generate documentation mapping from Nablarch official documentation to nabledge knowledge file structure.

## Workflow Steps

### Step 1: Generate Base Mapping (Path-based Classification Only)

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping.py v6
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v6.md`

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

### Step 2: Assign Processing Patterns (Content-based)

**Critical**: This step reads file content to determine Processing Pattern for ALL files.

**Processing Pattern MUST be determined by reading content, NOT by path patterns.**

**Approach**:

1. **Identify files requiring PP assignment**:
   - Read current mapping file
   - List all files by Type and Category
   - Focus on: development-tools/*, component/libraries, component/handlers

2. **For each file, read content and assign PP**:
   - Read source RST file (first 50-100 lines)
   - Apply rules from `references/content-judgement.md`
   - Look for indicators in title, first paragraph, examples
   - Assign PP based on content, NOT path

3. **Document assignments**:
   - Create assignment list with reasoning
   - File path → PP → Reason (indicators found)

4. **Update generate-mapping.py**:
   - Add content-reading logic
   - Implement PP assignment based on content indicators
   - Ensure reproducibility (deterministic rules)

**Key categories requiring content reading**:
- `development-tools/testing-framework` (48 files) - Read title to identify pattern
- `development-tools/toolbox` (6 files) - Read what the tool targets
- `component/libraries` (49 files) - Read if pattern-specific
- `component/handlers` (specific cases) - Read if pattern-specific

**Expected outcome**:
- All files have PP assigned based on content
- Assignment rules documented in classification.md
- generate-mapping.py implements content-based logic

### Step 3: Validate Mapping

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/validate-mapping.py .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Expected result**: All checks pass

If any check fails:
1. Read the error message carefully
2. Identify which rule in `generate-mapping.py` needs correction
3. Fix the rule
4. Return to Step 1

### Step 4: Export to Excel

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/export-excel.py .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v6.xlsx`

This Excel file is for human review and is not used in automated workflows.

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
python .claude/skills/nabledge-creator/scripts/generate-mapping-checklist.py .claude/skills/nabledge-creator/output/mapping-v6.md --source-dir .lw/nab-official/v6/ --output .claude/skills/nabledge-creator/output/mapping-v6.checklist.md
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v6.checklist.md`

This checklist is used in the verification session (`verify-mapping-6` workflow) to confirm classification accuracy (including Processing Pattern) by reading RST content.

## Generation Session Complete

Hand off the checklist to the verification session. The verification workflow (`verify-mapping-6`) runs in a separate session to avoid context bias.

## Input Directories

```
.lw/nab-official/v6/nablarch-document/en/
.lw/nab-official/v6/nablarch-document/ja/
.lw/nab-official/v6/nablarch-system-development-guide/
```

## Output Files

```
.claude/skills/nabledge-creator/output/mapping-v6.md          # Markdown table
.claude/skills/nabledge-creator/output/mapping-v6.xlsx        # Excel table (human review)
.claude/skills/nabledge-creator/output/mapping-v6.checklist.md # Verification checklist
```

## Reference Files

You may need to read these files during Step 4 (review item resolution):

- `.claude/skills/nabledge-creator/references/classification.md` - Path pattern classification rules
- `.claude/skills/nabledge-creator/references/target-path.md` - Path conversion rules
- `.claude/skills/nabledge-creator/references/content-judgement.md` - Content-based judgement rules
