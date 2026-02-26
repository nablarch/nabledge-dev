# clean workflow

Delete generated files to restore clean state.

## Skill Invocation

```
nabledge-creator clean {version}
```

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

## Workflow Steps

Execute the clean script:

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```
