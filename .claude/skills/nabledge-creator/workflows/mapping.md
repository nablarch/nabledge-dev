# Mapping Generation Workflow

Generate documentation mapping from Nablarch official documentation to nabledge knowledge file structure.

## Workflow Steps

### Step 1: Generate Mapping

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping.py v6
```

**Output**: `references/mapping/mapping-v6.md`

**Exit codes**:
- 0: Completed successfully (no review items)
- 1: Completed with review items (proceed to Step 4)
- 2: Script error (fix and re-run)

If exit code is 1, review items will be printed to stdout in JSON format. Proceed to Step 4 to resolve them.

### Step 2: Validate Mapping

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/validate-mapping.py references/mapping/mapping-v6.md
```

**Expected result**: All checks pass

If any check fails:
1. Read the error message carefully
2. Identify which rule in `generate-mapping.py` needs correction
3. Fix the rule
4. Return to Step 1

### Step 3: Export to Excel

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/export-excel.py references/mapping/mapping-v6.md
```

**Output**: `references/mapping/mapping-v6.xlsx`

This Excel file is for human review and is not used in automated workflows.

### Step 4: Resolve Review Items

Execute this step ONLY if Step 1 reported review items (exit code 1).

Review items are files where path-based classification was insufficient. For each review item:

1. **Read context**:
   - Read the target RST file
   - Read other files in the same directory
   - Check `:ref:` references and `toctree` directives that point to or from this file

2. **Make decision**:
   - If you can determine the correct classification, add a rule to `references/classification.md`
   - Update `generate-mapping.py` to implement the new rule
   - Return to Step 1

3. **If uncertain**:
   - Report to human with detailed reasoning why classification is ambiguous
   - Include file path, context examined, and conflicting indicators

Do NOT guess. If the classification is genuinely ambiguous, human judgment is required.

### Step 5: Generate Verification Checklist

Execute the following command:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping-checklist.py references/mapping/mapping-v6.md --source-dir .lw/nab-official/v6/ --output references/mapping/mapping-v6.checklist.md
```

**Output**: `references/mapping/mapping-v6.checklist.md`

This checklist is used in the verification session (`verify-mapping-6` workflow) to confirm classification accuracy by reading RST content.

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
references/mapping/mapping-v6.md          # Markdown table
references/mapping/mapping-v6.xlsx        # Excel table (human review)
references/mapping/mapping-v6.checklist.md # Verification checklist
```

## Reference Files

You may need to read these files during Step 4 (review item resolution):

- `references/classification.md` - Path pattern classification rules
- `references/target-path.md` - Path conversion rules
- `references/content-judgement.md` - Content-based judgement rules
