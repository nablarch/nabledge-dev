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

### Step 1: Confirm version

Verify the version parameter is valid (6 or 5).

### Step 2: Delete knowledge files

```bash
find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f -delete
```

Keep `index.toon` intact.

### Step 3: Delete docs files

```bash
find .claude/skills/nabledge-{version}/docs -name "*.md" -type f -delete
```

Delete all markdown files including `README.md`.

### Step 4: Delete empty directories

```bash
find .claude/skills/nabledge-{version}/knowledge -type d -empty -delete
find .claude/skills/nabledge-{version}/docs -type d -empty -delete
```

### Step 5: Delete output files

```bash
rm -f .claude/skills/nabledge-creator/output/mapping-v{version}.md
rm -f .claude/skills/nabledge-creator/output/mapping-v{version}.checklist.md
rm -f .claude/skills/nabledge-creator/output/mapping-v{version}.xlsx
```

### Step 6: Report deletion summary

Output summary of what was deleted:
- Number of JSON files deleted
- Number of Markdown files deleted
- Number of output files deleted
- Directories cleaned

**Example Output**:
```
nabledge-{version} クリーン完了:
- 知識ファイル: 162個のJSONファイル削除
- ドキュメントファイル: 163個のMDファイル削除（README.md含む）
- 出力ファイル: 3個のファイル削除（mapping-v{version}.md, .checklist.md, .xlsx）
- 空ディレクトリ削除完了
- 保持: index.toon のみ
```

## Notes

- This operation is destructive and cannot be undone
- Always confirm version number before executing
- `index.toon` is preserved because it tracks "not yet created" entries
- Use this before regenerating all files from scratch
