# clean workflow

Delete generated files to restore clean state.

**IMPORTANT**: Follow ALL steps in this workflow file exactly as written. Do not skip steps or use summary descriptions from SKILL.md or other files. Read and execute each step according to the detailed instructions provided here.

## Skill Invocation

```
nabledge-creator clean {version}
```

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

## Progress Checklist Template

```
## nabledge-creator clean {version} - Progress

□ Execute clean script

**Started:** [timestamp]
**Status:** Not started
```

## Workflow Steps

Execute the clean script:

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Exit code | 0 | [code] | ✓/✗ |
| Knowledge files deleted | Count | [from script output] | ✓ |
| Doc files deleted | Count | [from script output] | ✓ |
| Mapping outputs deleted | Count | [from script output] | ✓ |

**How to measure:**
- Exit code: Check script return value
- File counts: Parse script output messages (e.g., "Deleted 0 JSON files" or "削除: 0個のJSONファイル")
- Note: If counts are 0, this means clean state already existed (this is normal and counts as success ✓)
