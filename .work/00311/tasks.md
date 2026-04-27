# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-28

## In Progress

### [A] 全シートの方針決めるための調査

**目標**: 全212シートについて「どの変換パターンを適用すべきか」を判断するために必要なデータを揃える。

**調査対象パターン**:
- **P1-1候補**: P1シート95枚のうち `_detect_header()` run_length 閾値を 3→2 に変えれば P1 化できるシートを特定
- **P2-1候補**: P2(c) 112枚のうち「列インデックス = 階層レベル」の列インデント構造があるシートを特定（残りは P2-2）
- **P2-3確定**: P2(b) 5枚（セル内 `\n` あり）は既知

**変換方針メモ（案A採用確定）**:
- P2-1 の列→見出し変換は「絶対列番号固定」を採用
  - col0→H1, col1→H2, col2→H3, col3以降→本文
  - 根拠: `1.概要`(col1始まり) で col3 が本文段落 → 相対化すると本文が H3 になってしまう

**Steps:**
- [x] `1.概要`・`マルチパートリクエストのサポート対応` の列構造を確認
- [x] 案A（絶対列固定）vs 案B（相対化）の変換プレビューを生成して比較 → 案A 採用
- [ ] P2(c) の残りシートについて列インデント構造の有無を判定するスクリプトを作成・実行
  - 対象: useful_width≥4 の prose 系シート（`HIDDENストア脆弱性`、`別紙_分割後jarの取り込み`、`使用不許可APIチェックツールの設定方法` 等）
  - 判定基準: 同一行で複数列にデータが分散していれば列インデント構造あり → P2-1、そうでなければ P2-2
- [ ] P1シート95枚について run_length=2 で P1 化できる候補を特定
  - `バージョンアップ手順`系（col0空き＋col1=No＋col2=手順）が主候補
  - 閾値変更の副作用（誤検出増加）も確認
- [ ] 調査結果を `.work/00311/sheet-investigation-p2-1.md` に記録

## Not Started

### [B] 全シートの対応方針表の作成と承認

**目標**: [A] の調査結果を元に全212シートの変換方針を `.work/00311/sheet-mapping.md` にまとめ、承認を得る。

**成果物**:
- `.work/00311/sheet-mapping.md` — 全シートの対応方針表

**表構成**:

| バージョン | ファイル | シート | 現在 | 変換後 | 対応パターン | 備考 |
|-----------|--------|--------|------|--------|------------|------|

**対応パターン**:
- **P1-1**: `_detect_header()` の run_length 閾値を 3→2 に変更して P1 化
- **P2-1**: 絶対列インデックス → Markdown 見出しレベルに変換（col0=H1, col1=H2, col2=H3, col3以降=本文）
- **P2-2**: 現状維持（列インデント構造なし）
- **P2-3**: セル内 `\n` を Markdown 改行（`  \n`）として保持

**Steps:**
- [ ] [A] の調査結果を元に全212シートの方針を表にまとめる
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
