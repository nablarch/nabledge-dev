# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-28

## In Progress

### [E] Expert review & PR 作成

**Steps:**
- [ ] Expert review (Software Engineer + QA Engineer) — 実装レビュー
- [ ] Finding があれば修正
- [ ] PR 作成 via `/pr create`

## Done

- [x] [D] 設計書通りに実装 — 全5バージョン verify 0 FAIL (`5384ebe89`)
  - v5 ダブルスペース問題: `5384ebe89` で解決済み (verify All files verified OK 確認)
  - docs MD 目視確認完了: P2-1 多列行 (`No  適用手順` 形式)、P2-3 セルLF展開 正常
- [x] [C] 設計書の更新と expert review — 完了済み
  - `rbkc-verify-quality-design.md` §3-3、`rbkc-converter-design.md` §8 更新 — `d1c612c67`
  - Expert review (Software Engineer) — 0 Finding — `.work/00311/review-by-software-engineer.md`
- [x] [B] 全シートの対応方針表の作成と承認 — `tools/rbkc/docs/xlsx-sheet-mapping.md` 生成、サンプル4種（P1/P2-1/P2-2/P2-3）作成・承認取得 — `fde8da01b`
- [x] Created feature branch `311-excel-docs-md-readability`
- [x] Created `.work/00311/tasks.md`
- [x] Created PR #314
- [x] 全バージョン・全Excelシート P1/P2 分類調査 — `.work/00311/xlsx-p2-investigation.md` — committed `153f214d1`
- [x] `1.概要`・`マルチパートリクエスト` の列構造確認、案A（絶対列固定）vs 案B（相対化）プレビュー比較 → 案A 採用確定
- [x] [A] 全シート調査完了 — P2-1: 16枚、P2-2: 96枚、P2-3: 5枚、P1-1: スコープ外 — committed `732b6d211`
