# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11

## In Progress

### Task 17: FAIL 内容の正当性確認 ← 次のタスク

**背景（前回やり直しの教訓）:**
- 前回は verify 追加 → FAIL 大量 → RBKC 修正 → 劣化、という最悪ループに陥り revert
- 今回の 683 FAIL（v6）が genuine RBKC バグか、verify の誤検知かを確認してから次に進む

**調査手順（推測禁止・事実確認のみ）:**

**Steps:**
- [ ] FAIL サンプル1: `:ref:\`universal_dao\`` について — labels.py が返す `section_title` の実際の値を確認（コードを読む）
- [ ] FAIL サンプル2: `libraries-universal-dao.json` の `sections[].title` 一覧を確認（ファイルを読む）
- [ ] FAIL サンプル3: `universal_dao.rst` の先頭を確認（ラベルが h1 直前か h2 直前かを確認）
- [ ] 上記3点の事実から FAIL が genuine RBKC バグか verify の誤検知かを判断
- [ ] 判断結果をユーザーに提示（推測なし・事実のみ）
- [ ] ユーザー承認後に fix 実施

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
