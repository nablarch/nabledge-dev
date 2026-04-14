# Notes

## 2026-04-14（動作確認セッション）

### 現在の状況

v6 動作確認を実施中。テスト環境で QA・CA を実行してプロンプトを観測・記録した。
以下の変更は **コミット済み・プッシュ済み**。テスト環境は未コミット変更あり（settings.json パターンの修正が必要）。

---

### コミット済みの変更

| コミット | 内容 |
|---|---|
| `a40e1d23` | fix: `prefill-template.sh` の `escape_sed()` バグ修正（`/` がsedデリミタと衝突） |
| `f401497b` | feat: `setup-cc.sh` に `add_skill_permissions()` 追加（`settings.json` に Allow パターンを書き込む） |
| `92b60602` | feat: `GUIDE-GHC.md` に GHC 向け設定例と注記を追加 |
| `55418b9e` | revert: `SKILL.md` の `allowed-tools: Bash` を削除（サブエージェント経由のため効果なし） |

---

### 動作確認で判明した問題

#### 1. `setup-cc.sh` の Allow パターンが不足・不正確

現在の `setup-cc.sh` に設定済みのパターン（一部不正確）：

```json
"Bash(bash scripts/full-text-search.sh *)",
"Bash(bash scripts/read-sections.sh *)",
"Bash(bash .claude/skills/nabledge-{v}/scripts/full-text-search.sh *)",
"Bash(bash .claude/skills/nabledge-{v}/scripts/read-sections.sh *)",
"Bash(.claude/skills/nabledge-{v}/scripts/generate-mermaid-skeleton.sh *)",
"Bash(.claude/skills/nabledge-{v}/scripts/prefill-template.sh *)"  ← 不正確
```

**不足・修正が必要なパターン**（`permission-patterns.md` 参照）：

| パターン | 用途 | 状態 |
|---|---|---|
| `Bash(REPO_ROOT=*)` | Step 0: 開始時刻記録 | **未追加** |
| `Bash(KNOWLEDGE_DIR=*)` | Step 2: hints チェック | **未追加** |
| `Bash(OUTPUT_PATH=*)` | prefill-template.sh の `$()` 呼び出し | **パターン修正必要**（現在 `Bash(.claude/.../prefill-template.sh *)` だが合致しない） |
| `Bash(UNIQUE_ID=*)` | Step 3.5: duration 計算 | **未追加** |
| `Bash(find *)` | 依存クラス検索 | **別 Issue**（パターンが広すぎる） |

→ `setup-cc.sh` の `add_skill_permissions()` を修正する必要あり

#### 2. `code-analysis.md` の 3 つのバグ（修正済み・未コミット）

| バグ | 修正内容 |
|---|---|
| ターゲット未指定時に聞かない | Step 1 で AskUserQuestion を明示 |
| Write ツールに `$OUTPUT_PATH` が渡せない | 実際のパス文字列を使うよう指示 |
| `{{DURATION_PLACEHOLDER}}` の sed 置換失敗 | sed デリミタを `\|` に変更、CRITICAL 注記追加 |

---

### 次にやること

1. **`setup-cc.sh` の `add_skill_permissions()` を修正**
   - `Bash(.claude/skills/nabledge-{v}/scripts/prefill-template.sh *)` → `Bash(OUTPUT_PATH=*)` に変更
   - `Bash(REPO_ROOT=*)`, `Bash(KNOWLEDGE_DIR=*)`, `Bash(UNIQUE_ID=*)` を追加

2. **テスト環境を更新して動作確認を再実行**
   - `setup-cc.sh` の変更をテスト環境に反映
   - `/n6 code-analysis ImportZipCodeFileAction` で許可プロンプトが出ないことを確認

3. **確認 OK なら残り4バージョン（1.2, 1.3, 1.4, 5）に同じ変更を横展開**
   - `setup-cc.sh` はバージョン共通なので変更不要
   - `workflows/code-analysis.md` のバグ修正を横展開
   - `plugin/GUIDE-GHC.md` への注記追加を横展開

4. **CHANGELOG 更新**（各バージョンの `[Unreleased]` に追記）

5. **別 Issue 起票**（`find` コマンドのスクリプト化）

6. **Expert Review → PR 作成**

---

### 別 Issue 候補

#### `find` コマンドのスクリプト化
code-analysis Step 1 で依存クラス検索に直接 `find` を使っており、許可プロンプトが出る。
`find-file.sh` を作成してワークフローから呼ぶことで allow パターンで制御可能。
→ `Bash(.claude/skills/nabledge-{v}/scripts/find-file.sh *)` で許可可能

---

### テスト環境

`/tmp/nabledge-pr178-test/nablarch-example-batch/`
- ローカルブランチのスキルをコピー済み
- `code-analysis.md` のバグ修正済み
- `settings.json` は古いパターンのまま（`setup-cc.sh` 修正後に更新が必要）
