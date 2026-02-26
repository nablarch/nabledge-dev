# clean ワークフロー

生成ファイルを削除してクリーンな状態に戻す。

## Skill Invocation

```
nabledge-creator clean {version}
```

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

## 削除対象

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

## ワークフロー手順

Execute the clean script:

```bash
python .claude/skills/nabledge-creator/scripts/clean.py {version}
```
