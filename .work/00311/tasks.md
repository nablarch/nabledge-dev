# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-28

## In Progress

### [D] 設計書通りに実装

**Status**: 実装完了、v6 verify 0 FAIL。v5 verify で P2-1 QO2 ダブルスペース問題 13 FAIL 残存。

**Steps:**
- [x] TDD: verify/docs ユニットテスト先行記述（P2-1/P2-3 関連）— 398 tests pass
- [x] `xlsx_common.py`: `load_sheet_subtype_map()`, `_build_p2_1_meta()`, `_build_p2_content_raw()`, `sheet_to_result(sheet_subtype)` 実装
- [x] `xlsx_releasenote.py` / `xlsx_security.py`: `convert(sheet_subtype=None)` 追加
- [x] `docs.py` の `_render_xlsx_p2()` 変更（P2-1 raw_lines/p2_base_col、P2-3 hard line break）
- [x] `run.py`: `_load_sheet_subtype_map()`, `_convert_and_write(sheet_subtype_map)`, meta serialization (p2_headings/p2_raw_lines/p2_base_col/sheet_subtype/p2_raw_content) 実装
- [x] verify.py: QO1 p2_headings 逐次照合, QO2 P2-1 per-line, QO2 P2-3 両辺正規化 (+ blank line 二重スペース collapse) 実装
- [x] v6 create + verify → 0 FAIL
- [ ] **[BLOCKED: 未調査]** v5 verify P2-1 QO2 ダブルスペース問題 13 FAIL を調査・修正
  - 症状: `'クライアント側  サーバ側'` (ダブルスペース入り行) が docs MD に見つからない
  - 原因仮説: docs.py `_render_xlsx_p2` が body 行を `"  ".join(...)` で結合 → ダブルスペース生成、
    verify が `line not in docs_md_text` で照合するが docs MD 上は別の形式になっている可能性
  - 調査手順: v5 該当 JSON と docs MD を直接比較し、docs MD 内の実際の文字列を確認する
  - 影響: v5 の P2-1 ボディ行（見出し以外の行）に2列以上データがある場合に発生する可能性
- [ ] v5/v1.4/v1.3/v1.2 create + verify → 0 FAIL（上記修正後）
- [ ] docs MD を目視確認（P2-1 変換結果が意図通りか）

### [C] 設計書の更新と expert review — 完了済み

**Steps:** (すべて完了)
- [x] `rbkc-verify-quality-design.md` §3-3 更新
- [x] `rbkc-converter-design.md` §8 更新（p2_headings 逐次照合仕様）— `d1c612c67`
- [x] Expert review (Software Engineer) — 0 Finding — `.work/00311/review-by-software-engineer.md`

### [E] Expert review & PR 作成

**Steps:**
- [ ] Expert review (Software Engineer + QA Engineer) — 実装レビュー
- [ ] Finding があれば修正
- [ ] PR 作成 via `/pr create`

## Done

- [x] [B] 全シートの対応方針表の作成と承認 — `tools/rbkc/docs/xlsx-sheet-mapping.md` 生成、サンプル4種（P1/P2-1/P2-2/P2-3）作成・承認取得 — `fde8da01b`
- [x] Created feature branch `311-excel-docs-md-readability`
- [x] Created `.work/00311/tasks.md`
- [x] Created PR #314
- [x] 全バージョン・全Excelシート P1/P2 分類調査 — `.work/00311/xlsx-p2-investigation.md` — committed `153f214d1`
- [x] `1.概要`・`マルチパートリクエスト` の列構造確認、案A（絶対列固定）vs 案B（相対化）プレビュー比較 → 案A 採用確定
- [x] [A] 全シート調査完了 — P2-1: 16枚、P2-2: 96枚、P2-3: 5枚、P1-1: スコープ外 — committed `732b6d211`
