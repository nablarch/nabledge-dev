# all workflow

Execute the complete workflow: clean, generate (mapping + knowledge), and verify (mapping + knowledge).

**IMPORTANT**: Follow ALL steps in this workflow file exactly as written. Do not skip steps or use summary descriptions from SKILL.md or other files. Read and execute each step according to the detailed instructions provided here.

## Skill Invocation

```
nabledge-creator all {version} [--filter "key=value"]
```

Where:
- `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5)
- `[--filter]` is optional, passed to knowledge workflow for partial generation

## Workflow Overview

This workflow executes all steps in sequence:

1. **Clean**
2. **Mapping**
3. **Verify Mapping**
4. **Knowledge**
5. **Verify Knowledge**

See each step's workflow file in `workflows/` for detailed instructions.

## Progress Checklist Template

At workflow start, copy and display this checklist:

```
## nabledge-creator all {version} - Progress

□ Step 1: Clean
□ Step 2: Mapping
□ Step 3: Verify Mapping
□ Step 4: Knowledge
□ Step 5: Verify Knowledge

**Started:** [timestamp]
**Status:** Not started
**Filter:** [if provided, else "None - full generation"]
```

Update this checklist at each step boundary (mark → when starting, ✓ when complete).

## Session Management

**What this workflow does**: Executes ALL 5 steps in the current session immediately.

**About "separate session"**: Verification steps ideally run in a NEW CONVERSATION (fresh session) to avoid context bias from generation logic. However, this "all" workflow executes verification in the CURRENT SESSION for convenience.

**Alternative**: To run verification without context bias, use individual workflows in separate conversations instead of "all" workflow.

## Workflow Steps

### Step 1: Clean

Execute clean workflow. See `workflows/clean.md` for detailed steps.

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Exit code | 0 | [code] | ✓/✗ |
| Directories cleaned | 3 (knowledge, docs, output) | [count] | ✓ |

### Step 2: Generate Mapping

Execute mapping workflow. See `workflows/mapping.md` for detailed steps.

**Completion Evidence for Steps 2-5 (Mapping Generation):**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Files enumerated | >0 | [from generate-mapping.py output] | ✓ |
| Files mapped | [enumerated count] | [row count in mapping-v{version}.md] | ✓/✗ |
| Review items | 0 | [from generate-mapping.py output] | ✓/✗ |
| Validation | PASS | [from validate-mapping.py] | ✓/✗ |
| Excel exported | Yes | [mapping-v{version}.xlsx exists] | ✓ |
| Checklist generated | Yes | [mapping-v{version}.checklist.md exists] | ✓ |

### Step 6: Verify Mapping

Execute verify-mapping workflow. See `workflows/verify-mapping.md` for detailed steps.

**Note on session separation**: Ideally this runs in a separate session (new conversation) to avoid context bias. However, for convenience, this workflow executes it in the current session.

**Decision point**:
- If issues found, fix mapping generation logic and return to Step 2
- If mapping verified, proceed to Step 7

### Step 7: Generate Knowledge Files

Execute knowledge workflow. See `workflows/knowledge.md` for detailed steps.

**Completion Evidence for Step 7 (Knowledge Generation):**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Targets identified | [from mapping / filter] | [count] | ✓ |
| JSON files generated | [targets count] | [ls *.json \| wc -l] | ✓/✗ |
| MD files generated | [JSON count] | [ls *.md \| wc -l] | ✓/✗ |
| JSON validation | PASS | [validate-knowledge.py result] | ✓/✗ |
| index.toon entries | [JSON count] | [entries in index.toon] | ✓/✗ |
| index.toon validation | PASS | [validate-index.py result] | ✓/✗ |

### Step 8: Verify Knowledge Files

Execute verify-knowledge workflow. See `workflows/verify-knowledge.md` for detailed steps.

**Note on session separation**: Ideally this runs in a separate session (new conversation) to avoid context bias. However, for convenience, this workflow executes it in the current session.

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

2. **Session separation**: This workflow executes verification in the current session. For unbiased verification, run individual workflows (`/nabledge-creator verify-mapping {version}`) in new conversations instead.

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
