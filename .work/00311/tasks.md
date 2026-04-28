# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-28

## In Progress

### [F] P2-1 ####-本文バグの調査・設計・修正

PR #314 マージ後に発覚したバグ（実装前から存在）。

**状況**:
- 影響シート（全バージョン網羅調査済み）:
  - v5: `security-check-1.概要` — **既存コミット済みMDが既に壊れている**（offset=2の15行が `####` 見出しになっている）
  - v6: `security-check-1.概要` — 再生成すると壊れる
  - v6: `マルチパートリクエストのサポート対応` — 再生成すると壊れる
- v1.2/v1.3/v1.4 は該当なし

**根本原因**:
- `_build_p2_1_meta` (xlsx_common.py) が `offset <= 2 → p2_headings/####` と判定
- `security-check-1.概要` は H2(col=1)/H3(col=2)/本文(col=3) の3段構造
  → col=3 は offset=2 になり本文が `####` 見出しに誤変換される
- `マルチパートリクエストのサポート対応` も同様（H2/H3/本文の3段構造）
- Excelのインデント構造はシートごとに異なるため「offset=2は必ず見出し」という前提が成立しない

**検討方針（未決定）** [DECISION: あるべき姿を検討してから実装]:
- 対処療法でなくあるべき姿を設計してから実装すること
- キーとなる問いは「P2-1シートで何が見出しで何が本文かをどう判定するか」

**Steps:**
- [ ] あるべき設計の検討（expert consultation 含む）[DECISION: 設計方針の確定が必要]
- [ ] 設計書更新（rbkc-converter-design.md §8）
- [ ] TDD: verify テスト追加（RED）
- [ ] 実装修正（GREEN）
- [ ] 全5バージョン create + verify 0 FAIL 確認
- [ ] v5 security-check-1.概要 の MD が正常になっていることを目視確認
- [ ] commit & push

## Done

- [x] [E] Expert review & PR 作成 — SE impl 0 Findings, QA 0 Findings (1 fixed: §3-4 table), PR #314 updated — `75e9d7920`
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
