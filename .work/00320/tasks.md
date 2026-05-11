# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev12)

## In Progress

（なし）

## Not Started

（なし）

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
- [x] 設計書 P2-4 記述を復元 — ブランチ分岐点が #327 マージ前だったため消えていた — `21fd36c59`
- [x] Task 18: 横並びチェック完了 — docutils 不使用の RST 構造解析なし（修正不要）
- [x] 最終エキスパートレビュー完了 — SE: 0 Findings、QA: 0 Findings — PR #330 Expert Review 更新済み — `f9b694bf5`
