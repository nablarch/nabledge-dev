# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-29

## In Progress

### [B] 全シートの対応方針表の作成と承認

**目標**: [A] の調査結果を元に全212シートの変換方針を `tools/rbkc/docs/xlsx-sheet-mapping.md` にまとめ、承認を得る。

**対応パターン**:
- **P2-1**: 絶対列インデックス → Markdown 見出しレベルに変換（col0=H1, col1=H2, col2=H3, col3以降=本文）
- **P2-2**: 現状維持（テーブル構造、単列リスト等）
- **P2-3**: セル内 `\n` を Markdown 改行（`  \n`）として保持
- **P1-1 なし**: スコープ外（低効果）

**Steps:**
- [x] 全212シートの方針を表にまとめる → `.work/00311/sheet-mapping.md`（生成済み）
- [x] sheet-mapping.md を `tools/rbkc/docs/xlsx-sheet-mapping.md` に移動（`current` 列削除、設計情報として整形）
- [x] 各パターンの複雑な代表シートの変換サンプルを生成して提示
  - P2-1: `マルチパートリクエストのサポート対応`（v6）、`HIDDENストア脆弱性`（v5）
  - P2-2: `バージョンアップ手順`（v5u5）
  - P2-3: `バージョンアップ手順`（v6u2、Maven LF）、`3.PCIDSS対応表`（v6）
- [ ] ユーザーに提示して承認取得

### [C] 設計書の更新と expert review

**目標**: [B] 承認済みの方針を `rbkc-converter-design.md` §8 に反映し、3軸の品質を担保した仕様に仕上げる。
3軸: ① 知識ファイル JSON の content 品質、② verify 設計書 (QC1/QC2/QC3) への影響、③ 閲覧用 docs MD の可読性。

**Steps:**
- [ ] `rbkc-verify-quality-design.md` で P2 関連チェック（QC1/QC2/QC3/QP）を確認
- [ ] P2-1/P2-3 変換仕様が verify チェックに与える影響を分析（content トークン変化 → QC1 閾値影響など）
- [ ] docs MD 閲覧用の変換仕様も設計書に含める（JSON と docs MD で出力が異なる場合は明示）
- [ ] `rbkc-converter-design.md` §8 を更新（対応パターン定義 + sheet-mapping.md へのリンク）
- [ ] Expert review (Software Engineer) — 設計書レビュー
- [ ] Finding があれば修正し再レビュー
- [ ] ユーザーに最終確認

### [D] 設計書通りに実装

**Steps:**
- [ ] TDD: verify ユニットテストを先に書く（P2-1/P2-3 関連チェックが変わる場合）
- [ ] `xlsx_common.py` の `_detect_header()` 変更（P1-1 対応、閾値 3→2）
- [ ] `xlsx_common.py` の `_build_p2_content()` 変更（P2-1: 列→見出し変換、P2-3: LF 保持）
- [ ] `docs.py` の `_render_xlsx_p2()` 変更（P2-1/P2-3 対応）
- [ ] 全5バージョンで `create → verify` を実行し FAIL 差分確認
- [ ] docs MD を目視確認（P2-1 変換結果が意図通りか）

### [E] Expert review & PR 作成

**Steps:**
- [ ] Expert review (Software Engineer + QA Engineer) — 実装レビュー
- [ ] Finding があれば修正
- [ ] PR 作成 via `/pr create`

## Done

- [x] Created feature branch `311-excel-docs-md-readability`
- [x] Created `.work/00311/tasks.md`
- [x] Created PR #314
- [x] 全バージョン・全Excelシート P1/P2 分類調査 — `.work/00311/xlsx-p2-investigation.md` — committed `153f214d1`
- [x] `1.概要`・`マルチパートリクエスト` の列構造確認、案A（絶対列固定）vs 案B（相対化）プレビュー比較 → 案A 採用確定
- [x] [A] 全シート調査完了 — P2-1: 16枚、P2-2: 96枚、P2-3: 5枚、P1-1: スコープ外 — committed `732b6d211`
