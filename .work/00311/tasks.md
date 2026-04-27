# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-27

## In Progress

### [A] 全Excelファイル × シート一覧の対応方針表を設計書に記載

**目標**: 全バージョン・全ファイル・全シートについて「このシートはどう変換するか」をひと目でわかる表として `rbkc-converter-design.md` に追加する。

**表の構成（案）**:

| バージョン | ファイル | シート | 現在 | 変更後 | 対応パターン | 備考 |
|-----------|--------|--------|------|--------|------------|------|
| v6 | `Nablarch機能のセキュリティ対応表.xlsx` | `3.PCIDSS対応表` | P2 | P1 | P1-1: run_length≥2に変更 | 2列表 |
| v6 | `nablarch6u1-releasenote.xlsx` | `バージョンアップ手順` | P2 | P1 | P1-1: run_length≥2に変更 | 2列表 |
| v6 | `Nablarch機能のセキュリティ対応表.xlsx` | `1.概要` | P2 | P2 | P2-1: 列インデント→見出し変換 | 散文・列インデント構造あり |
| v6 | `nablarch6u2-releasenote.xlsx` | `バージョンアップ手順` | P2 | P1 | P1-1 + P2-3: セル内\n保持 | 2列表 + Mavenアーティファクト一覧 |
| ... | ... | ... | ... | ... | ... | ... |

**対応パターン定義（設計書に記載する内容）**:
- **P1-1**: `_detect_header()` の run_length 閾値を 3 → 2 に変更してP1化
- **P2-1**: 列インデックス → Markdown 見出しレベルに変換（散文シートの構造を復元）
- **P2-2**: 現状維持（散文・列インデントなし）
- **P2-3**: セル内 `\n` を改行として保持

**Steps:**
- [ ] `rbkc-converter-design.md` の §8 を読み、表を追加する適切な場所を確認
- [ ] 調査済みデータ（`.work/00311/xlsx-p2-investigation.md`）を元に全117 P2シートの対応方針を決定し表を作成
  - P1-1 対象：約46シート（2列表）
  - P2-1 対象：列インデント構造があるシートを特定して一覧化
  - P2-2 対象：現状維持でよいシートを一覧化
  - P2-3 対象：セル内 `\n` あり5シートを一覧化（P1-1 と組み合わせを含む）
- [ ] `1.概要`・`マルチパートリクエストのサポート対応` の実際の列構造を確認し P2-1 の変換ルールを具体化
  （何列目がどのレベルの見出しになるか、`【】` 見出しパターンはどう扱うか）
- [ ] 表と対応パターン定義を `rbkc-converter-design.md` §8 に追記
- [ ] ユーザーに提示して承認取得
- [ ] [DECISION: P2-1の列インデント→見出し変換ルール（列番号固定 or 相対化）を承認後確定]

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
