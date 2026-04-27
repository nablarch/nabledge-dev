# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-27

---

## 現状

- 22-B-12 code changes は commit 済 (`4b6d598f1`, `9b3d5d032`, `2e45cea4d`, `3dd3d483f`)
- **全 5 バージョン verify FAIL 0** 確認済
- 377 tests GREEN
- nabledge-test runner は model: sonnet 固定 (`nabledge-test-runner.md` frontmatter)
- PR #304 push 済 — **v6/v5 knowledge/docs 再生成済み** (`93fa83ea2`, `0d013db6e`)

---

## In Progress

### knowledge/docs 再生成

v6/v5 完了。残り v1.4/v1.3/v1.2 を 1 バージョンずつ実施。

**Steps:**
- [x] v6 create (353ファイル) + verify OK + commit/push — `93fa83ea2`
- [x] v5 create (533ファイル) + verify OK + commit/push — `0d013db6e`
- [ ] v1.4 create + verify OK + 差分チェック(knowledge/docs のみ) + commit/push
- [ ] v1.3 create + verify OK + 差分チェック(knowledge/docs のみ) + commit/push
- [ ] v1.2 create + verify OK + 差分チェック(knowledge/docs のみ) + commit/push

## Not Started

### kc (knowledge-creator) および関連ファイルの削除

RBKC が kc を完全置換したため、kc ツール本体・キャッシュ・レポート・テスト・関連 rule を削除する。

**対象 (削除予定):**
- `tools/knowledge-creator/` 全体
- `.claude/rules/knowledge-creator.md`
- CLAUDE.md / README.md / setup.sh / `.gitignore` から kc 参照を除去

**Steps:**
- [ ] 依存参照の洗い出し (`grep -rln "knowledge-creator\|tools/knowledge-creator\|kc\.sh"`)
- [ ] `tools/knowledge-creator/` 削除
- [ ] `.claude/rules/knowledge-creator.md` 削除
- [ ] CLAUDE.md / README.md / setup.sh / `.gitignore` から kc 参照を除去
- [ ] `tools/tests/test-setup.sh` 等から kc チェックを除去
- [ ] 全 5 バージョン `rbkc create + verify` FAIL 0 維持確認
- [ ] 377 tests GREEN 維持確認
- [ ] commit & push

## Done

- [x] 22-B-12 実装 (Finding A/B/C + ws3) — `4b6d598f1`, `9b3d5d032`, `2e45cea4d`, `3dd3d483f`
- [x] v1.4 mapping `document/` prefix 修正 — `69a876c19`
- [x] Sphinx-follow policy (ERROR/3 → warning) spec + 実装 — `f1009f243`, `dadfcea13`
- [x] v1.4/v1.3/v1.2 知識ファイル再生成 — `ed8161f10`, `3b7515ce3`, `fb0cc138a`
- [x] nabledge-5/1.4/1.3/1.2 skill 構造を v6 に同期 — `b06d8cf23`
- [x] v6 nabledge-test baseline 取得 (20260424-172654)
- [x] v5/1.4/1.3/1.2 qa-001 smoke baseline 取得 (20260424-201710)
- [x] setup スクリプト: 旧 skill dir 削除してから cp — `d496683bf`
- [x] RBKC README 現状構成に書き直し — `66a23db94`
- [x] CHANGELOG `[Unreleased]` ルールベース化追記 — `fac51b221`
- [x] `work-log.md` に `.work/` は常に git 対象である旨追記
