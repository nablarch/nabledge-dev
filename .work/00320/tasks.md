# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev9)

## In Progress

（なし）

## Not Started

### Task 18: 横並びチェック — docutils を使わない RST 構造解析が他にないか

**背景:**
- `_scan_rst_labels` の自作行スキャンが今回の問題の原因
- 同様の問題が他にないか確認し、あれば修正する
- **調査済みの事実（本タスク着手不要の確認済み箇所）:**
  - `verify.py` の `check_source_links` / `check_external_urls` → docutils AST 使用済み ✅
  - `rst_ast_visitor.py` → docutils AST を基盤とする設計 ✅
  - `verify.py` の `_RST_HEADING_UNDERLINE_RE` (QC5) → 目的が「RST 残存チェック」であり構造解析ではない（docutils 不要）✅
  - `_scan_rst_labels` → Task 17 で修正済み ✅

**Steps:**
- [ ] `scripts/` 全体を grep して、RST ファイルを読み込んで自作 regex / 行スキャンで構造（heading / label / section）を解析している箇所を列挙
- [ ] 各箇所について「docutils AST で代替すべきか」を判断
- [ ] 要修正箇所があれば TDD で修正
- [ ] 要修正なければ「なし」と記録して完了

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
  - リバート理由: verify が「リンク先存在チェック」のみで「意図したリンクか」を検証しておらず、
    RBKC の heading 修正が正しいリンクを壊しても FAIL しなかった
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
- [x] Task 16: verify check_source_links() cross-doc 実装 — SE: 1 Finding fixed, QA: 0 Findings
- [x] Task 17: `_scan_rst_labels` docutils AST 化 + subtitle sections[0] 修正 — 全5バージョン 0 FAIL、SE: 0 Findings、QA: 2 Findings fixed
- [x] Task 17 完了: 設計書 §4 QL1 マトリクス ✅、PR #330 Success Criteria 全4項目 ✅ Met
