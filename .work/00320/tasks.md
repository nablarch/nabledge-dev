# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11

## In Progress

### Task 17: FAIL 内容の正当性確認 ← 次のタスク

**背景（前回やり直しの教訓）:**
- 前回は verify 追加 → FAIL 大量 → RBKC 修正 → 劣化、という最悪ループに陥り revert
- 今回の 683 FAIL（v6）が genuine RBKC バグか、verify の誤検知かを確認してから次に進む

**疑問点:**
- 全 FAIL が `section_title 'XXX' not found in yyy.json sections[]` パターン
- 例: `:ref:\`universal_dao\`` → `section_title='ユニバーサルDAO'` が `libraries-universal-dao.json sections[]` にない
- 原因仮説: `labels.py` が h1 ラベルに `section_title=h1タイトル` をセットするが、RBKC は h1 を `sections[]` ではなく JSON `title` フィールドに出力する
- 前回の revert 前に `373a6d4cd fix: h1-level labels resolve to document-level reference (section_title="")` というコミットがあった（revert で消えた）
- その fix が正しければ：h1 ラベルは `section_title=""` にすべきで、そうすれば section チェックがスキップされ FAIL は消える
- verify のロジックが正しければ RBKC 側（labels.py）を fix すべき、verify を弱めてはいけない

**Steps:**
- [ ] FAIL サンプル調査: `:ref:\`universal_dao\`` の labels.py 解決値を確認（`section_title` が h1 か否か）
- [ ] `about-nablarch-big-picture.json` の `sections[]` を確認（`全体像` がなぜ absent か）
- [ ] 前回リバート前の `373a6d4cd` の内容を確認（h1 label fix の実装）
- [ ] verify ロジックが正しいか / labels.py を fix すべきか判断してユーザーに提示
- [ ] ユーザー承認後に labels.py 修正 or verify 修正

### Task 16: 実装（完了）

**Steps（完了済み）:**
- [x] TDD: `TestCheckSourceLinks_JsonSide` テスト追加（RED）
- [x] `verify.py` — `_section_titles_from_json()` + cross-doc JSON side 実装（GREEN）
- [x] TDD: `TestCheckSourceLinks_DocsMdSide` テスト追加（RED）
- [x] `verify.py` — `_heading_slugs_from_md()` + cross-doc docs MD side 実装（GREEN）
- [x] `run.py` に `knowledge_dir`, `docs_dir` 引数追加
- [x] 全5バージョン verify 実行、FAIL diff 確認・記録（v6:683, v5:688, v1.4:125, v1.3:113, v1.2:126）
- [x] Expert review (Software Engineer + QA Engineer) — SE: 1 Finding fixed（json_key dedup バグ）, QA: 0 Findings
- [x] 設計書 §4 マトリクス QL1 状態ノート追加（⚠️ 維持 — 条件3: RBKC fix 未完）
- [x] CHANGELOG 更新不要（verify 内部改善、エンドユーザー向け変化なし）

## Not Started

### Task 17: PR 最終確認・マージ

**Steps:**
- [ ] PR #330 の Success Criteria チェック
- [ ] PR 更新（Expert Review リンク追加）

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
  - リバート理由: verify が「リンク先存在チェック」のみで「意図したリンクか」を検証しておらず、
    RBKC の heading 修正が正しいリンクを壊しても FAIL しなかった
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
