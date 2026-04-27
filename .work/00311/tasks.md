# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-27

## In Progress

### [A] 全Excelファイル × シート一覧の対応方針表を作成

**目標**: 全バージョン・全ファイル・全シートについて「このシートはどう変換するか」を
`.work/00311/sheet-mapping.md`（別ファイル）にまとめ、`rbkc-converter-design.md` §8 からはリンクのみ張る。

**成果物**:
- `.work/00311/sheet-mapping.md` — 全シートの対応方針表（承認用）
- `rbkc-converter-design.md` §8 — 対応パターン定義 + `sheet-mapping.md` へのリンク

**sheet-mapping.md の表構成**:

| バージョン | ファイル | シート | 現在 | 変更後 | 対応パターン | 備考 |
|-----------|--------|--------|------|--------|------------|------|

**対応パターン定義（設計書 §8 に記載する内容）**:
- **P1-1**: `_detect_header()` の run_length 閾値を 3 → 2 に変更してP1化
- **P2-1**: 列インデックス → Markdown 見出しレベルに変換（散文シートの構造を復元）
- **P2-2**: 現状維持（散文・列インデントなし）
- **P2-3**: セル内 `\n` を改行として保持

**Steps:**
- [x] `1.概要`・`マルチパートリクエストのサポート対応` の実際の列構造を確認
  - `1.概要`: col1=シートタイトル, col2=H2相当見出し, col3=本文, col4–=詳細データ（最大col9まで）
  - `マルチパートリクエストのサポート対応`: col0=■タイトル, col1=【】見出し(H2相当), col2=【】小見出し or 本文(H3相当), col3=箇条書き本文, col4=コード/パスリスト, col5=プロパティ名（深いインデント）
  - 両シートとも「列インデックス = 階層レベル」の純粋な列インデント構造
  - `【】` パターンは見出しマーカーとして列2以上に出現（装飾ではなく構造）
  - `■` パターンは最上位タイトルとして列0に出現
- [DECISION: P2-1の変換ルール案を承認してください]
  - **案A（列番号固定）**: col0=■→H1、col1=【】→H2、col2=【】or本文→H3、col3以降=本文
    → シンプルだがファイルをまたいで列ずれがあると崩れる
  - **案B（相対化）**: シート内で実際に使われている最小列インデックスを0として相対化
    → ファイル依存なく安定するが実装がやや複雑
  - 推奨: **案B**（`1.概要` は col1 始まり、`マルチパートリクエスト` は col0 始まり → 絶対列番号では揃わない）
- [ ] 調査済みデータ（`.work/00311/xlsx-p2-investigation.md`）を元に `.work/00311/sheet-mapping.md` を作成
  - 全212シートを網羅（P1/P2問わず）
  - P1-1 対象：約46シート（2列表）
  - P2-1 対象：列インデント構造があるシートを特定して一覧化
  - P2-2 対象：現状維持でよいシートを一覧化
  - P2-3 対象：セル内 `\n` あり5シートを一覧化
- [ ] `rbkc-converter-design.md` §8 に対応パターン定義と `sheet-mapping.md` へのリンクを追記
- [ ] ユーザーに提示して承認取得

## Not Started

### [C] Excel → JSON → MD 変換設計

**目標**: [A] の対応方針表が承認されたら、verify 設計書・検索への影響まで考慮して変換仕様を確定する。

**Steps:**
- [ ] verify 設計書（`rbkc-verify-quality-design.md`）でP2関連チェックを確認
- [ ] 変換仕様変更が verify の QC1/QC2/QC3/QP チェックに与える影響を分析
- [ ] 検索品質への影響を確認（JSON content がどう変わるか）
- [ ] 変換仕様を設計書ドラフトとして作成（`rbkc-converter-design.md` §8 更新）
- [ ] ユーザーに提示して承認取得

### [D] 設計書更新と実装

**Steps:**
- [ ] `tools/rbkc/docs/rbkc-converter-design.md` §8 を更新（承認済み仕様を反映）
- [ ] TDD: verify ユニットテストを先に書く（必要な場合）
- [ ] `xlsx_common.py` の `_detect_header()` 変更（P1-1対応）
- [ ] `xlsx_common.py` の `_build_p2_content()` 変更（P2-1/P2-3対応）
- [ ] `docs.py` の `_render_xlsx_p2()` 変更（P2-1/P2-3対応）
- [ ] 全5バージョンで `create → verify` を実行し FAIL 差分確認
- [ ] docs MD を目視確認

### [E] Expert review & PR creation

**Steps:**
- [ ] Expert review (Software Engineer + QA Engineer)
- [ ] Fix any Findings
- [ ] Create PR via `/pr create`

## Done

- [x] Created feature branch `311-excel-docs-md-readability`
- [x] Created `.work/00311/tasks.md`
- [x] Created PR #314
- [x] 全バージョン・全Excelシート P1/P2 分類調査 — `.work/00311/xlsx-p2-investigation.md` — committed `153f214d1`
