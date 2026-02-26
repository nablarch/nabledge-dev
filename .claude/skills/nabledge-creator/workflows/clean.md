# clean workflow

Delete generated files to restore clean state.

## Skill Invocation

```
nabledge-creator clean {version}
```

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

## Deletion Targets

### 1. Knowledge Files
- Location: `.claude/skills/nabledge-{version}/knowledge/`
- Delete: All `*.json` files (recursively)
- Keep: `index.toon` (do not delete)

### 2. Docs Files
- Location: `.claude/skills/nabledge-{version}/docs/`
- Delete: All `*.md` files (recursively) including `README.md`

### 3. Output Files
- Location: `.claude/skills/nabledge-creator/output/`
- Delete:
  - `mapping-v{version}.md`
  - `mapping-v{version}.checklist.md`
  - `mapping-v{version}.xlsx`

## Workflow Steps

Execute the clean script:

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```
