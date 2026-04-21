# Tasks: Allow scripts no-permission-prompt (#178)

**PR**: #305
**Issue**: #178
**Branch**: 178-allow-scripts-no-permission-prompt
**Updated**: 2026-04-15

## PR 変更ファイル一覧（2026-04-15 確認）

`git diff --name-only origin/main...HEAD` の結果。現時点は v6 のみ変更済み。

| ファイル（`.claude/skills/nabledge-6/` 以下） | 変更種別 | 伝播対象 | 想定差分（v6 との比較） |
|---|---|---|---|
| `plugin/CHANGELOG.md` | v6 固有 | 不要 | — |
| `plugin/GUIDE-CC.md` | 追記 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}`（本文 2 箇所） |
| `plugin/GUIDE-GHC.md` | 追記 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}`（本文 1 箇所） |
| `scripts/finalize-output.sh` | 新規 | 5, 1.2, 1.3, 1.4 | 完全一致 |
| `scripts/find-file.sh` | 新規 | 5, 1.2, 1.3, 1.4 | 完全一致 |
| `scripts/get-hints.sh` | 新規 | 5, 1.2, 1.3, 1.4 | 完全一致（`SKILL_DIR` は `$SCRIPT_DIR/..` で自動解決） |
| `scripts/prefill-template.sh` | バグ修正（`escape_sed`） | 5, 1.2, 1.3, 1.4 | 完全一致 |
| `scripts/read-file.sh` | 新規 | 5, 1.2, 1.3, 1.4 | 完全一致 |
| `scripts/record-start.sh` | 新規 | 5, 1.2, 1.3, 1.4 | 完全一致 |
| `workflows/_knowledge-search/_full-text-search.md` | パス修正 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}`（スクリプトパス 1 箇所） |
| `workflows/_knowledge-search/_section-judgement.md` | 複数変更 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}` ＋ 内容変更（pipe→colon 注記・Step 0 スクリプト化・output 例） |
| `workflows/code-analysis.md` | 複数変更 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}` ＋ 多数の内容変更（Step 0/1/3 スクリプト化、AskUserQuestion 追加など） |
| `workflows/qa.md` | パス修正 | 5, 1.2, 1.3, 1.4 | `nabledge-6` → `nabledge-{v}`（スクリプトパス 1 箇所） |
| `.pr/00178/notes.md` | 作業ログ | 不要 | — |
| `.pr/00178/permission-patterns.md` | 作業ログ | 不要 | — |
| `.pr/00178/tasks.md` | 作業ログ | 不要 | — |
| `tools/setup/setup-cc.sh` | 共有スクリプト | 伝播済み（全バージョン共通ファイル） | — |
| `tools/setup/setup-ghc.sh` | 共有スクリプト | 伝播済み（全バージョン共通ファイル） | — |

## In Progress

_（なし）_

## Not Started

_（なし）_

## Done (追加分)

- [x] Task #1: Copy 5 scripts + prefill-template.sh fix to nabledge-5/1.2/1.3/1.4 — commit `ee167ed4`
- [x] Task #2: code-analysis.md propagated to nabledge-5/1.2/1.3/1.4 — commit `15dba23f`
- [x] Task #3: _section-judgement.md propagated — commit `99762ae2`
- [x] Task #4: GUIDE-GHC.md (auto-approval + known issue) propagated — commit `d9858d42`
- [x] Task #6: _full-text-search.md / qa.md absolute paths propagated — commit `a3e76954`
- [x] Task #7: GUIDE-CC.md auto-approval section propagated — commit `b619984e`
- [x] Task #8: Diff check — all ✅ (NABLEDGE_BRANCH 差分は既存・意図的)
- [x] Task #5: Expert Review (Prompt Engineer 4/5) + PR #305 updated — commits `91957410`, `08a8df9c`

## Archived: Not Started (2026-04-15)

### [Task #1] Cross-version: scripts を nabledge-5/1.2/1.3/1.4 に追加

差分確認済み（2026-04-15）: 全バージョンで 5 スクリプトすべて未追加。

**スクリプト一覧:**
- `get-hints.sh` — KNOWLEDGE_DIR パスがバージョン固有なので要調整
- `record-start.sh` — 全バージョン共通
- `finalize-output.sh` — 全バージョン共通
- `find-file.sh` — 全バージョン共通
- `read-file.sh` — 全バージョン共通

**Steps:**
- [ ] Copy 5 scripts to nabledge-5, 1.2, 1.3, 1.4 (adjust `get-hints.sh` KNOWLEDGE_DIR)
- [ ] Verify file permissions are 755
- [ ] Commit per version (or batch commit)

### [Task #2] Cross-version: code-analysis.md を nabledge-5/1.2/1.3/1.4 に反映

差分確認済み（2026-04-15）: 全バージョンで inline bash が残存、スクリプト呼び出しへの移行が未。

**変更内容（全バージョン共通）:**
1. 冒頭に「Bash usage: restricted commands only」注意書きを追加
2. Step 0 の inline bash → `record-start.sh` 呼び出しに置き換え
3. 「Confirm analysis target」ステップ（AskUserQuestion）を追加（nabledge-6 行 25-38 相当）
4. Step 1 の Glob/Grep → `find-file.sh` / `read-file.sh` 呼び出しに置き換え
5. Step 3.2 の `prefill-template.sh` に `bash` prefix を追加
6. Step 3.5-4 の Write パス注意書き追加（`$OUTPUT_PATH` ではなく実パスを渡す旨）
7. Step 3.5-5 の duration 計算 inline bash → `finalize-output.sh` 呼び出しに置き換え

**Steps:**
- [ ] Update nabledge-5 code-analysis.md
- [ ] Update nabledge-1.2 code-analysis.md
- [ ] Update nabledge-1.3 code-analysis.md
- [ ] Update nabledge-1.4 code-analysis.md
- [ ] Commit

### [Task #3] Cross-version: _section-judgement.md を nabledge-5/1.2/1.3/1.4 に反映

差分確認済み（2026-04-15）: 全バージョンで pipe→colon 注記なし、Step 0 が inline bash のまま。

**変更内容:**
1. Input セクションに pipe→colon 変換注記を追加
2. Step 0 の inline `for` ループ bash → `get-hints.sh` 呼び出しに置き換え
3. Output 例の section_id を数値 ID 形式（`s3`, `s1`）に更新

**ファイルパス:** `workflows/_knowledge-search/_section-judgement.md`

**Steps:**
- [ ] Update all 4 versions
- [ ] Commit

### [Task #4] Cross-version: GUIDE-GHC.md を nabledge-5/1.2/1.3/1.4 に反映

差分確認済み（2026-04-15）: 全バージョンで auto-approval セクション・known issue セクションなし。

**変更内容:**
1. 「コマンドの自動承認について」セクション追加（nabledge-6 行 82-87 相当）
2. 「terminal awaiting input」known issue セクション追加（nabledge-6 行 94-103 相当）

**Steps:**
- [ ] Update all 4 versions
- [ ] Commit

### GitHub Actions 確認結果（2026-04-15）

**対応不要。** 根拠:
- `sync-manifest.txt` の `dir .claude/skills/nabledge-6/scripts` エントリが新スクリプトをカバー済み
- 新スクリプトは全て `100755` で git 登録済み（`cp -r` で同期先にもパーミットが保持される）
- CI テストワークフローは存在しない（従来から同様）

### [Task #6] Cross-version: _full-text-search.md / qa.md のスクリプトパスを nabledge-5/1.2/1.3/1.4 に反映

差分確認済み（2026-04-15）: `bash scripts/xxx.sh`（相対パス）のまま。nabledge-6 では絶対パスに変更済み。

**変更内容:**
- `_full-text-search.md`: `bash scripts/full-text-search.sh` → `bash .claude/skills/nabledge-{v}/scripts/full-text-search.sh`
- `qa.md`: `bash scripts/read-sections.sh` → `bash .claude/skills/nabledge-{v}/scripts/read-sections.sh`

**Steps:**
- [ ] Update all 4 versions (_full-text-search.md, qa.md)
- [ ] Commit

### [Task #7] Cross-version: GUIDE-CC.md の「自動承認」セクションを nabledge-5/1.2/1.3/1.4 に反映

差分確認済み（2026-04-15）: 「コマンドの自動承認について」セクションが未追加。

**挿入内容（nabledge-6 行 71-77 相当、`{v}` はバージョンに置換）:**
```
## コマンドの自動承認について

nabledge-{v} が実行するコマンドのうち...
```

**Steps:**
- [ ] Update all 4 versions
- [ ] Commit

### [Task #8] 全バージョン変更後の差分チェック ← Task #1〜#4, #6, #7 完了後に実施

**検証方法:** 各バージョンを nabledge-6 と `diff` し、上記「PR 変更ファイル一覧」表の「想定差分」列と一致することを確認。想定外差分は修正する。

```bash
# 完全一致確認（scripts）
diff .claude/skills/nabledge-6/scripts/record-start.sh \
     .claude/skills/nabledge-5/scripts/record-start.sh

# バージョン名置換のみ確認（workflows/docs）
diff .claude/skills/nabledge-6/workflows/qa.md \
     .claude/skills/nabledge-5/workflows/qa.md
```

**許容される差分:** `nabledge-6` → `nabledge-{v}` の置換のみ
**許容されない差分:** inline bash 残存、スクリプトパス未修正、想定外テキスト差分

**対象ファイル（各バージョン × 4）:**
- `scripts/` 以下の全ファイル（5新規 + `prefill-template.sh`）
- `workflows/code-analysis.md`
- `workflows/qa.md`
- `workflows/_knowledge-search/_full-text-search.md`
- `workflows/_knowledge-search/_section-judgement.md`
- `plugin/GUIDE-CC.md`
- `plugin/GUIDE-GHC.md`

### [Task #5] Expert Review → PR 最終化

**Steps:**
- [ ] Run expert review per `.claude/rules/expert-review.md`
- [ ] Save to `.pr/00178/review-by-*.md`
- [ ] Create PR with `Skill(skill: "pr", args: "create")`

## Done

- [x] Fix `prefill-template.sh` escape_sed() bug (`/` as sed delimiter) — commit `a40e1d23`
- [x] Add `add_skill_permissions()` to `setup-cc.sh` with correct patterns — commits `f401497b`, `2ef28263`
- [x] Add GHC no-prompt-confirmation notes to `nabledge-6/plugin/GUIDE-GHC.md` — commit `92b60602`
- [x] Revert `allowed-tools: Bash` from nabledge-6 SKILL.md (ineffective via sub-agent) — commit `55418b9e`
- [x] Extract inline bash into dedicated scripts for nabledge-6 (`get-hints.sh`, `record-start.sh`, `finalize-output.sh`) — commit `3e18e857`
- [x] Use full-path script calls in nabledge-6 workflows — commit `0eab2c7e`
- [x] Fix bash prefix for `generate-mermaid-skeleton.sh` and `prefill-template.sh` — commit `99aa64d8`
- [x] Fix `finalize-output.sh` using lowercase target name for output path — commit `30a92c0f`
- [x] Fix `prefill-template.sh` call as single-line command (no pipe/multiline) — commit `af1bbae2`
- [x] Prevent agent from absolutizing script paths in workflows — commit `07a943b5`
- [x] Add required target confirmation step before code-analysis — commit `ff69d5a1`
- [x] Consolidate bash command rules and use run-verbatim fence in nabledge-6 — commit `ad561b6d`
