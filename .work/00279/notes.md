# Notes

## 2026-03-30

### Step 1: v0.7以降のコミット分析

v0.7リリース (`e86d668f`, 2026-03-27) 以降のコミットをsync-manifestと照合した結果。

#### ユーザー影響あり（デプロイ対象）

| コミット | 内容 | 対象プラグイン |
|---------|------|--------------|
| `06450f5c` feat: generate nabledge-1.3 knowledge files and baseline (#247) | `.claude/skills/nabledge-1.3/` 全体、`.claude/commands/n1.3.md`、`.github/prompts/n1.3.prompt.md` | nabledge-1.3 |
| `13aed100` feat: generate nabledge-1.2 knowledge files and baseline (#248) | `.claude/skills/nabledge-1.2/` 全体、`.claude/commands/n1.2.md`、`.github/prompts/n1.2.prompt.md` | nabledge-1.2 |

#### ユーザー影響なし（デプロイ対象外）

| コミット | 理由 |
|---------|------|
| `9b4c2b2a` fix: treat missing command/prompt files as FAIL in test-setup.sh | `tools/` — sync-manifest対象外 |
| `1cd89c10`, `82029b48`, `439dc21f` chore: update metrics report | `docs/` — sync-manifest対象外 |
| `ea4401e2` feat: align Adoption x-axis | `docs/` — sync-manifest対象外 |
| `212ad189` fix: align SLOC trend x-axis | `docs/` — sync-manifest対象外 |
| `0256ee6e`, `2222f6c7` nabledge-5 troubleshooting / v0.2 release | v0.7リリース済み |

#### バージョン案

- nabledge-1.3: **v0.1**（初回リリース）
- nabledge-1.2: **v0.1**（初回リリース）
- marketplace: **v0.8**（前回v0.7からインクリメント）

### Step 2: CHANGELOG案（レビューフィードバック反映後の現在の状態）

**nabledge-1.3 CHANGELOG**:
```
## [0.1] - 2026-03-30

### 追加

- Nablarch 1.3の全ドキュメントをカバーする知識ファイルを追加しました。
```

**nabledge-1.2 CHANGELOG**:
```
## [0.1] - 2026-03-30

### 追加

- Nablarch 1.2の全ドキュメントをカバーする知識ファイルを追加しました。
```
