# all workflow

Execute the complete workflow: clean, generate (mapping + knowledge), and verify (mapping + knowledge).

## Skill Invocation

```
nabledge-creator all {version} [--filter "key=value"]
```

Where:
- `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5)
- `[--filter]` is optional, passed to knowledge workflow for partial generation

## Workflow Overview

This workflow executes all steps in sequence:

1. **Clean** - Delete all generated files for clean state
2. **Mapping** - Generate documentation mapping with Type/Category/PP classification
3. **Verify Mapping** - Verify mapping classification accuracy (separate session recommended)
4. **Knowledge** - Generate knowledge files (JSON + MD) and update index.toon
5. **Verify Knowledge** - Verify knowledge files content accuracy (separate session recommended)

## Progress Checklist Template

At workflow start, copy and display this checklist:

```
## nabledge-creator all {version} - Progress

□ Step 1: Clean
□ Step 2: Mapping
□ Step 3: Verify Mapping (optional)
□ Step 4: Knowledge
□ Step 5: Verify Knowledge (optional)

**Started:** [timestamp]
**Status:** Not started
**Filter:** [if provided, else "None - full generation"]
```

Update this checklist at each step boundary (mark → when starting, ✓ when complete).

## Session Management

**Generation steps (clean, mapping, knowledge)** can run in a single session.

**Verification steps (verify-mapping, verify-knowledge)** should ideally run in separate sessions to avoid context bias. However, for convenience, this workflow executes them immediately after generation.

**Recommendation**: For critical verification, run verify-mapping and verify-knowledge manually in fresh sessions after generation completes.

## Workflow Steps

### Step 1: Clean

Execute clean workflow to delete all generated files:

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```

**Deleted files**:
- Knowledge files: `.claude/skills/nabledge-{version}/knowledge/*.json`
- Documentation: `.claude/skills/nabledge-{version}/docs/*.md`
- Mapping outputs: `.claude/skills/nabledge-creator/output/mapping-v{version}.*`

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Exit code | 0 | [code] | ✓/✗ |
| Directories cleaned | 3 (knowledge, docs, output) | [count] | ✓ |

See `workflows/clean.md` for detailed completion criteria.

### Step 2: Generate Mapping

Execute mapping workflow to generate documentation mapping:

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping.py "v{version}"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`

**Exit code handling**:
- Exit 0: Success - Proceed to Step 3
- Exit 1: Review items exist - Resolve review items before proceeding
- Exit 2: Script error - Fix and retry

If exit code 1, follow review item resolution process in `mapping.md` workflow before proceeding.

### Step 3: Validate Mapping

```bash
python .claude/skills/nabledge-creator/scripts/validate-mapping.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md"
```

**Expected**: All checks pass. If failed, fix issues in generate-mapping.py and return to Step 2.

### Step 4: Export Mapping to Excel

```bash
python .claude/skills/nabledge-creator/scripts/export-excel.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v{version}.xlsx`

### Step 5: Generate Mapping Verification Checklist

```bash
python .claude/skills/nabledge-creator/scripts/generate-mapping-checklist.py ".claude/skills/nabledge-creator/output/mapping-v{version}.md" --source-dir ".lw/nab-official/v{version}/" --output ".claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md"
```

**Output**: `.claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md`

**Completion Evidence for Steps 2-5 (Mapping Generation):**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Files enumerated | >0 | [from generate-mapping.py output] | ✓ |
| Files mapped | [enumerated count] | [row count in mapping-v{version}.md] | ✓/✗ |
| Review items | 0 | [from generate-mapping.py output] | ✓/✗ |
| Validation | PASS | [from validate-mapping.py] | ✓/✗ |
| Excel exported | Yes | [mapping-v{version}.xlsx exists] | ✓ |
| Checklist generated | Yes | [mapping-v{version}.checklist.md exists] | ✓ |

See `workflows/mapping.md` for detailed completion criteria for each sub-step.

### Step 6: Verify Mapping (Optional in Same Session)

**Note**: Ideally run in separate session to avoid context bias. For convenience, this workflow executes verification immediately.

Execute verify-mapping workflow following the checklist generated in Step 5. See `verify-mapping.md` for detailed verification process.

**Decision point**:
- If issues found, fix mapping generation logic and return to Step 2
- If mapping verified, proceed to Step 7

### Step 7: Generate Knowledge Files

Execute knowledge workflow to generate knowledge files:

**Step 7.1: Identify Targets**

Read mapping file and extract targets matching filter (if provided).

**Step 7.2: Generate Knowledge Files**

For each target, follow the process in `knowledge.md` workflow:
- Read RST sources
- Determine section IDs
- Extract hints (file-level and section-level)
- Convert to JSON
- Output to `.claude/skills/nabledge-{version}/knowledge/{path}.json`

**Step 7.3: Markdown Conversion**

```bash
python scripts/convert-knowledge-md.py .claude/skills/nabledge-{version}/knowledge/ --output-dir .claude/skills/nabledge-{version}/docs/
```

**Step 7.4: Validation**

```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-{version}/knowledge/
```

If validation fails, fix JSON files and re-execute from Step 7.3.

**Step 7.5: Update index.toon**

Aggregate file-level hints and update index.toon:

1. Aggregate hints from all sections in each JSON file
2. Update corresponding entry in `.claude/skills/nabledge-{version}/knowledge/index.toon`
3. Validate format:
   ```bash
   python scripts/validate-index.py .claude/skills/nabledge-{version}/knowledge/index.toon
   ```
4. Verify status consistency:
   ```bash
   python scripts/verify-index-status.py .claude/skills/nabledge-{version}/knowledge/index.toon
   ```

**Step 7.6: Generate Knowledge Verification Checklists**

For each generated knowledge file:

```bash
python scripts/generate-checklist.py .claude/skills/nabledge-{version}/knowledge/{file}.json --source .lw/nab-official/v{version}/nablarch-document/en/{source-path} --output .claude/skills/nabledge-{version}/knowledge/{file}.checklist.md
```

**Completion Evidence for Step 7 (Knowledge Generation):**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Targets identified | [from mapping / filter] | [count] | ✓ |
| JSON files generated | [targets count] | [ls *.json \| wc -l] | ✓/✗ |
| MD files generated | [JSON count] | [ls *.md \| wc -l] | ✓/✗ |
| JSON validation | PASS | [validate-knowledge.py result] | ✓/✗ |
| index.toon entries | [JSON count] | [entries in index.toon] | ✓/✗ |
| index.toon validation | PASS | [validate-index.py result] | ✓/✗ |

See `workflows/knowledge.md` for detailed completion criteria for each sub-step.

### Step 8: Verify Knowledge Files (Optional in Same Session)

**Note**: Ideally run in separate session to avoid context bias. For convenience, this workflow executes verification immediately.

Execute verify-knowledge workflow following the process in `verify-knowledge.md`:

**Step 8.1: Read Input Files**
- Mapping file
- Knowledge schema
- Generated knowledge files

**Step 8.2: Verify All Knowledge Files**

For each file:
- Read source RST documentation
- Verify schema compliance
- Verify content accuracy
- Verify keyword coverage
- Record results

**Step 8.3: Verify index.toon Integration**
- File-level hints verification
- Format validation
- Status consistency check

**Step 8.4: Categorize Issues**
- Schema violations (Critical)
- Content gaps (High Priority)
- Keyword deficiencies (Medium Priority)
- index.toon integration issues (High Priority)

**Step 8.5: Document Verification Results**

Create verification report at `.pr/{issue_number}/knowledge-verification-results.md`.

**Decision point**:
- If verification PASSED: Workflow complete
- If verification FAILED: Exit and fix in new generation session

**Completion Evidence for Step 8 (Knowledge Verification):**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Files verified | [JSON files count from Step 7] | [verification count] | ✓/✗ |
| Schema violations | 0 | [Critical issues count] | ✓/✗ |
| Content accuracy | All pass | [High priority issues count] | ✓/✗ |
| index.toon integration | All pass | [issues count] | ✓/✗ |

See `workflows/verify-knowledge.md` for detailed completion criteria.

## Output Files

After successful execution:

**Mapping files**:
```
.claude/skills/nabledge-creator/output/mapping-v{version}.md
.claude/skills/nabledge-creator/output/mapping-v{version}.xlsx
.claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md
```

**Knowledge files**:
```
.claude/skills/nabledge-{version}/knowledge/*.json
.claude/skills/nabledge-{version}/docs/*.md
.claude/skills/nabledge-{version}/knowledge/index.toon
.claude/skills/nabledge-{version}/knowledge/*.checklist.md
```

**Verification results**:
```
.pr/{issue_number}/mapping-verification-results.md (if verify-mapping executed)
.pr/{issue_number}/knowledge-verification-results.md (if verify-knowledge executed)
```

## Notes

1. **Filter usage**: If `--filter` is provided, only matching knowledge files are generated. Mapping generation always processes all files.

2. **Session separation**: While this workflow executes verification in the same session for convenience, running verify-mapping and verify-knowledge in separate sessions provides better verification quality by avoiding context bias.

3. **Error handling**: If any step fails, fix the issue and resume from that step. No need to restart from clean.

4. **Review items**: If mapping generation reports review items (exit code 1), resolve them before proceeding to knowledge generation.

5. **Partial regeneration**: For partial updates, use individual workflows (knowledge, verify-knowledge) instead of all workflow.

## When to Use This Workflow

**Use "all" workflow when**:
- Starting fresh knowledge base creation
- Major updates requiring full regeneration
- Verifying entire workflow integrity
- Testing workflow changes

**Use individual workflows when**:
- Updating specific knowledge files
- Fixing issues found in verification
- Iterative development and testing
- Partial regeneration with --filter
