# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-28 (updated)

## In Progress

### [G] リベース＋スコープ外変更の調査・対応

差分チェックにより、PR #314 には Issue #311 スコープ外の変更が含まれることが判明。
リベースして解消する。

**背景**:
- ブランチが `origin/main` の `8f37ab917` から分岐
- その後 PR #315 (Issue #312) が `origin/main` にマージ (`c430898c9`)
- `4b11e55c3` で `create 5` / `create 6` を全再生成した際、PR #315 の変更（RST block_quote 修正）が v5/v6 の非P2-1ファイルに取り込まれた
- → P2-1/P2-3 非対象の docs 341ファイル + knowledge JSON 372ファイルが差分として発生

**Steps:**
- [x] `origin/main` へリベース — merge-base が `c430898c9` (origin/main最新) と一致、リベース不要と判明
- [x] リベース後の差分を確認 — スコープ外 330 docs MD + 351 knowledge JSON（PR #315の内容と同一、内容は正しい）
- [x] 知識 JSON 372件を再生成 — `4b11e55c3` は docs MD のみで JSON は未再生成だった（QO2 418 FAIL）→ 全5バージョン再生成して修正 — `fe2765c37`
- [x] 全5バージョン verify 0 FAIL 確認 — v6/v5/v1.4/v1.3/v1.2 All files verified OK
- [x] diff-check.md を更新 — `55a746a86`
- [ ] push --force-with-lease

## Done

- [x] [F] P2-1 ####-本文バグ修正 — 絶対列＋単一セル条件で判定、全5バージョン verify OK — `4b11e55c3`
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
