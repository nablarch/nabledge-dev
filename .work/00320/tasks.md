# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-08

## In Progress

### Task 16: 実装

**設計（Task 15 完了・ユーザー承認済み）:**
- `labels.py` の `build_label_doc_map()` は `file_id`, `section_title`, `type`, `category`, `anchor` を持つ `LabelTarget` を返す（既存・main 済み）
- `run.py` は verify パスで `build_label_doc_map()` を使い、`label_map` に完全な `LabelTarget` を持っている（既存）
- `check_source_links()` にクロスドキュメント検証を追加:
  - シグネチャに `knowledge_dir=None`, `docs_dir=None` を追加
  - `:ref:` で `LabelTarget.file_id` が非空のとき、4 点検証（target JSON 存在・section_title 照合・target docs MD 存在・anchor slug 照合）
  - display-text `:ref:` にも同じ 4 点チェックを適用
- `run.py` に `knowledge_dir=output_dir, docs_dir=docs_dir` を `check_source_links()` 呼び出しに追加
- ヘルパー（module レベル）: `_section_titles_from_json()`, `_heading_slugs_from_md()`
- テストクラス: `TestCheckSourceLinks_JsonSide`, `TestCheckSourceLinks_DocsMdSide`（spec §4 対応テスト表の通り）

**Steps:**
- [ ] TDD: `TestCheckSourceLinks_JsonSide` テスト追加（RED）
- [ ] `verify.py` — `_section_titles_from_json()` + cross-doc JSON side 実装（GREEN）
- [ ] TDD: `TestCheckSourceLinks_DocsMdSide` テスト追加（RED）
- [ ] `verify.py` — `_heading_slugs_from_md()` + cross-doc docs MD side 実装（GREEN）
- [ ] `run.py` に `knowledge_dir`, `docs_dir` 引数追加
- [ ] 全5バージョン create + verify 実行、FAIL diff 確認・記録
- [ ] Expert review (Software Engineer + QA Engineer)
- [ ] 設計書 §4 マトリクス QL1 を ✅ に更新
- [ ] CHANGELOG 更新

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
