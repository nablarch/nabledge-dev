# Tasks: Fix security checklist Excel merged-row grouping (#347)

**PR**: #348
**Issue**: #347
**Updated**: 2026-05-22 (updated end-of-session)

## Rule: Fact-based judgment only

すべての調査・作業・判断は事実ベースで行う。コードを読んで「おそらく〜のはず」という推測で進めない。
- 各タスクの着手前に: 関連ファイルを実際に読み、コマンドを実行して事実を確認する
- 判断の根拠をすべて notes.md に記録する（"確認したコマンドと出力" の形式で）
- 不明点があれば推測して進まず、調査してから進む

---

## In Progress

(なし)

---

## Not Started

### ~~Task 1: ベースライン記録 — 全5バージョンの verify FAIL 数を記録~~ ✅
**Steps:**
- [x] `bash rbkc.sh verify 6` 実行、FAIL 0 件
- [x] `bash rbkc.sh verify 5` 実行、FAIL 0 件
- [x] `bash rbkc.sh verify 1.4` 実行、FAIL 0 件
- [x] `bash rbkc.sh verify 1.3` 実行、FAIL 0 件
- [x] `bash rbkc.sh verify 1.2` 実行、FAIL 0 件
- [x] 結果を `.work/00347/notes.md` に記録
- [x] コミット: `docs: record baseline verify FAIL counts for #347` — `108d9bc5b`

---

### Task 2: 設計 — 修正方針の設計書作成とユーザー確認
**前提調査（完了）:**
- [x] Excel の `2.チェックリスト` シートで `ws.merged_cells.ranges` を全列挙し、タイトル列（C 列）のマージ範囲を特定する
  - C列に12グループ（脆弱性単位）のマージあり（rows 9-13=SQLi, 14-15=OSコマンド, ... 56-57=アクセス制御）
- [x] `openpyxl` の `MergedCellRange` API を確認 — `ws.merged_cells.ranges` で列挙、`m.min_col/max_col/min_row/max_row` で範囲特定
- [x] 現在の `_build_p1_sections` の section 生成ロジックを正確に把握する
  - `xlsx_common.py:487-540`：1データ行→1セクション生成（マージ無視）

**設計（確定）:**
- [x] 修正アプローチを決定: **Option A（RawSheetに`merged_col_groups`フィールド追加）**
  - Software Engineer expert review 実施: 0 Findings — Option A推奨
  - Option B（forward-fill）は`read_sheet()`がタイトル列を知れないため不採用
  - 発動条件: `data_start`以降のタイトル列がrow-spanningマージのslaveである行のみグループ化
  - 全量調査（RBKC mapped xlsx全29ファイル全シート）実施: 影響は`2.チェックリスト` 4シートのみ（v5/v6 各日/英）
  - リリースノートのヘッダ行マージ（パターンA）・非タイトル列マージ（パターンC）は発動しない
- [DECISION: この設計で進めてよいか] `tools/rbkc/docs/rbkc-converter-design.md` §8-4 P1 `sections`行に新挙動を追記する
- [ ] `tools/rbkc/docs/xlsx-sheet-mapping.md` の `2.チェックリスト` 行（v5/v6両方）に Notes 追加
- [ ] `tools/rbkc/docs/rbkc-verify-quality-design.md` への影響: **変更不要**（Excel QC1-QC3はセル値ベース、セクション境界非依存）
- [ ] `tools/rbkc/docs/rbkc-json-schema-design.md` への影響: **変更不要**（スキーマ構造は変わらない）

**⚠️ ユーザー承認待ち — 設計承認後にコミット・次タスクへ進む**
- [ ] コミット: `docs: design for merged-row P1 grouping in security checklist (#347)`

**調査ファクト（notes.md参照）:**
- 全量調査スクリプト実行済み: 37シートにタイトル列行マージあり、うちデータ行マージ（P1に影響）は`2.チェックリスト`と`改訂履歴`/`Revision History`のみ
- `改訂履歴`はヘッダ行内マージ（data_start前）→発動しない
- verify FAILリスク: なし（集約後も全セル値は section.content に `{列名}: {値}` 形式で含まれる）

---

### Task 3: 閲覧用MD プレビュー生成とユーザー確認（実装前）
*閲覧用MDで見栄えに関する変更のため、実装前に期待出力を確認する*

**Steps:**
- [ ] 期待出力のプロトタイプを生成するスクリプトを `.work/00347/` に作成する（本番コードではなく one-off）
- [ ] プロトタイプを実行して期待 docs MD を生成する
  - ファクト確認: 生成された MD のセクション数・タイトルを確認
- [ ] 期待 docs MD を `.work/00347/preview-security-check-2-checklist.md` に保存する
- [ ] コミット: `docs: preview expected security-check-2 docs MD (#347)`
- [ ] プッシュ

**⚠️ ユーザー確認が必要 — PRでユーザーに閲覧用MDを確認してもらう**

---

### Task 4: TDD — 失敗するテストを追加
*TDD ルール: 実装前にテストを書き RED を確認すること*

**Steps:**
- [ ] `tools/rbkc/tests/ut/test_xlsx_common.py` を新規作成（またはテスト対象ファイルを確認）
- [ ] `_build_p1_sections` での merged-row グループ化を検証するテストを追加する
  - テスト設計: タイトル列がマージされている場合、同一マージグループの行が1セクションになること
  - エッジケース: グループ内に空行がある場合、複数のマージグループが連続する場合
- [ ] `pytest` 実行 → RED を確認
- [ ] コミット: `test: add failing tests for merged-row P1 grouping (#347)`

---

### Task 5: 実装 — merged-row グループ化を `xlsx_common.py` に追加
*Task 2 の設計・Task 3 のユーザー確認・Task 4 の RED テストが完了してから着手すること*

**Steps:**
- [ ] `tools/rbkc/scripts/create/converters/xlsx_common.py` を修正する
  - `read_sheet` でマージセル情報を保持するか、`_build_p1_sections` でグループ化するかは設計に従う
- [ ] `pytest` 実行 → GREEN を確認（新テスト + 既存テスト全通過）
- [ ] コミット: `feat: group merged-row cells in P1 section builder (#347)`

---

### Task 6: RBKC create+verify 全5バージョン実行 — FAIL 差分確認
*Task 1 のベースラインと比較する*

**Steps:**
- [ ] `bash rbkc.sh create v6 && bash rbkc.sh verify v6` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh create v5 && bash rbkc.sh verify v5` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh create v1.4 && bash rbkc.sh verify v1.4` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh create v1.3 && bash rbkc.sh verify v1.3` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh create v1.2 && bash rbkc.sh verify v1.2` 実行、FAIL 数を記録
- [ ] Task 1 との差分を `.work/00347/notes.md` に記録する
  - 期待: security-check-2 の FAIL 減少、他バージョンへの影響なし
  - 予期しない増加がある場合: 原因を特定して修正してから先に進む

---

### Task 7: 更新された knowledge ファイルをコミット
*Task 6 で verify が clean（または想定内の変化のみ）になってから着手すること*

**Steps:**
- [ ] `git diff --stat` で変更されたファイルを確認し、想定外のファイルが含まれないことを確認
- [ ] v6 の更新ファイルをステージング・コミット: `chore: regenerate security-check-2 knowledge files v6 (#347)`
- [ ] v5 の更新ファイルをステージング・コミット: `chore: regenerate security-check-2 knowledge files v5 (#347)`

---

### Task 8: Expert review — QA Engineer + Software Engineer
**Steps:**
- [ ] QA Engineer expert review を subagent で実施（テストカバレッジ・エッジケース評価）
- [ ] Software Engineer expert review を subagent で実施（設計品質・コード品質評価）
- [ ] Finding があればすべて修正する（横断チェック含む）
  - Finding が出た場合: 水平チェックを行い同じ根本原因の箇所を全件修正する
- [ ] 結果を `.work/00347/review-by-qa-engineer.md` と `.work/00347/review-by-software-engineer.md` に保存する

---

### Task 9: 変更差分チェック — 想定変更のみかを確認
*全ての実装・expert review 後、PR レビュー依頼前に実施する*

**Steps:**
- [ ] `git diff origin/main --stat` を実行して全変更ファイルを列挙する
- [ ] 各ファイルの変更が今回の Issue #347 のスコープ内であることを確認する
  - 想定変更: `xlsx_common.py`、テストファイル、knowledge ファイル (v5/v6)、設計書、`.work/00347/`
  - 想定外変更: 他バージョンの knowledge ファイル（意図しない変更）、設計書以外のルールファイル等
- [ ] チェック結果を `.work/00347/diff-check.md` に記録する
- [ ] コミット: `docs: diff check result for #347`

**⚠️ ユーザー確認が必要 — チェック結果をPRで提示してユーザーに確認を求める**

---

### Task 10: PR レビュー依頼
**Steps:**
- [ ] Task 9 のユーザー確認完了後、PR に expert review リンクを追加する
- [ ] PR の Success Criteria Check テーブルを更新する
- [ ] ユーザーにレビュー依頼する

---

## Done

- [x] Issue #347 調査: Excel 構造・RBKC パイプライン・現状の出力を確認 — コミット不要（タスクリスト作成の前提調査）

---

## Issue #347 との対応

| SC | 対応タスク |
|----|-----------|
| SQLインジェクション等の脆弱性を聞くと、その脆弱性1件分の全情報が1セクションで返る（チェックリスト全体ではなく脆弱性単位） | Task 5 (グループ化実装) + Task 6 (verify 確認) |
| すべての脆弱性エントリが名前で参照可能・無意味なタイトルなし | Task 5 (グループ化実装) |
| 同じ Excel ソースの他の knowledge ファイルへの影響なし | Task 6 (全5バージョン verify で確認) |
| 根本原因が再現可能なテストで特定される | Task 4 (TDD) |
| テスト環境で解決を確認 | Task 6 (verify GREEN) |
| 同様の構造を持つ他 Excel シートの水平チェック | Task 2 (設計) + Task 6 (全バージョン verify) |
| 再発防止措置 | Task 4 (テスト) + Task 2 (設計書更新) |
