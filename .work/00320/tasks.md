# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev2)

## In Progress

### Task 17: labels.py h1 section_title バグ修正 ← 次のタスク

**調査結果（事実）:**
- v6 FAIL 701件 = すべて QL1
  - 692件: `section_title not found in sections[]`（JSON side）
  - 9件: `anchor` 不一致（docs MD side）
- 692件の根本原因: labels.py が h1 ラベルの `section_title` に h1 テキストをセットしているが、
  設計書 §3-2-1 の仕様は「top-level なら空文字」— これが verify 誤検知の原因
- 9件の anchor 不一致は genuine RBKC バグ（別途確認要）

**修正方針（設計書 §3-2-1 準拠）:**
- `labels.py`: h1 ラベルは `section_title = ""`（top-level は空文字）
- `verify.py`: `section_title` が空のとき `sections[]` チェックをスキップ（JSON ファイル存在チェックのみ）

**Steps:**
- [ ] TDD: labels.py h1 ラベルの `section_title` が `""` になるテスト追加（RED）
- [ ] labels.py 修正: h1 ラベルの `section_title` を `""`（GREEN）
- [ ] TDD: verify.py `section_title` 空のとき `sections[]` スキップするテスト追加（RED）
- [ ] verify.py 修正（GREEN）
- [ ] 全5バージョン verify 実行、FAIL diff 確認（692件が消えること、9件 anchor FAILの内容確認）
- [ ] anchor 9件が genuine RBKC バグか verify 誤検知か確認・対処
- [ ] 全 FAIL 0件を確認
- [ ] 設計書 §4 マトリクス QL1 を ✅ に更新
- [ ] ユーザーに完了報告

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
