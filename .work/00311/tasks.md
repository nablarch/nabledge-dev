# Tasks: Excel-derived docs MD readability improvement

**PR**: #314
**Issue**: #311
**Updated**: 2026-04-27

## In Progress

### [A] パターン洗い出し（P1 / P2 両方）

**調査済み事項**:
- 全5バージョン・76ファイル・212シートを調査済み（`.work/00311/xlsx-p2-investigation.md`）
- P1: 95シート、P2: 117シート

**P2シートのパターン（表以外）**:

| パターン | 代表シート | 件数 | 問題 |
|---------|-----------|------|------|
| P2-1: 散文テキスト（列インデント構造あり） | `1.概要`、`マルチパートリクエストのサポート対応`、`件数取得SQLの拡張ポイント追加` | 多数 | 現在すべてフラットテキスト、セクション見出しや段落が失われる |
| P2-2: 散文テキスト（列インデントなし、本文のみ） | `HIDDENストア脆弱性`、`データベースアクセスの型変換機能削除の対応方法` など | 少数 | 現状でほぼ問題なし |
| P2-3: セル内 `\n` あり | `認可データ設定ツールのバージョンアップ方法`（XML 25行）、`バージョンアップ手順`（Maven一覧） | 5シート | `\n` がスペースに潰される |

**P1化対象（現在誤ってP2に分類されている表）**:

| パターン | 代表シート | 件数 | P2になっている理由 |
|---------|-----------|------|----------------|
| P1-1: 2列表（run_length=2） | `3.PCIDSS対応表`（v5/v6）、`バージョンアップ手順`（全バージョン約44枚） | 約46シート | `_detect_header()` の run_length ≥ 3 要件で検出失敗 |

**Steps:**
- [x] 全バージョンの全ExcelシートをP1/P2分類 — 調査完了
- [x] P2シートのパターン分類 — 上記テーブル参照
- [x] P1化対象（誤P2）の特定 — 上記テーブル参照
- [ ] `1.概要` と `マルチパートリクエストのサポート対応` の実際の列構造を確認し、P2-1 の列インデント→Markdown 見出し変換が成立するか検証
- [ ] `バージョンアップ手順` の全バージョン代表サンプルを確認し、P1化後のMDテーブルが読めるか検証

## Not Started

### [B] 各パターンの閲覧用MD マッピング設計

**目標**: パターンごとに「Excel セル → docs MD の何に対応するか」を決める

**Steps:**
- [ ] P1-1: `_detect_header()` の run_length 閾値 3 → 2 に変更したときの副作用を確認
  （他の散文シートが誤ってP1に昇格しないか全P2シートで検証）
- [ ] P2-1: 列インデント構造の MD マッピングを設計
  - 例：col_index を見出しレベルに対応させる案
  - 例：`【】` 囲み文字を見出しとして扱う案
  - 1パターンにするか複数パターンを使い分けるか決定
- [ ] P2-2: 現状維持で問題なしかを確認し、対応方針を決定
- [ ] P2-3: セル内 `\n` の扱いを決定（改行保持 or コードブロック化）
- [ ] マッピング案をユーザーに提示して承認取得

### [C] Excel → JSON → MD 変換設計

**目標**: マッピング設計を verify 設計書・検索への影響まで考慮して確定させる

**Steps:**
- [ ] verify 設計書（`rbkc-verify-quality-design.md`）でP2関連チェックを確認
- [ ] 変換仕様変更が verify の QC1/QC2/QC3/QP チェックに与える影響を分析
- [ ] 検索品質への影響を確認（JSON content がどう変わるか）
- [ ] 変換仕様を設計書ドラフトとして作成
- [ ] ユーザーに提示して承認取得

### [D] 設計書更新と実装

**Steps:**
- [ ] `tools/rbkc/docs/rbkc-converter-design.md` §8 を更新
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
- [x] 全バージョン・全Excelシート P1/P2 分類調査 — `.work/00311/xlsx-p2-investigation.md`
