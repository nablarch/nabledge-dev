# Tasks: Fix security checklist Excel merged-row grouping (#347)

**PR**: (TBD)
**Issue**: #347
**Updated**: 2026-05-22

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

### Task 1: ベースライン記録 — 全5バージョンの verify FAIL 数を記録
**Steps:**
- [ ] `bash rbkc.sh verify v6` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh verify v5` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh verify v1.4` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh verify v1.3` 実行、FAIL 数を記録
- [ ] `bash rbkc.sh verify v1.2` 実行、FAIL 数を記録
- [ ] 結果を `.work/00347/notes.md` に記録
- [ ] コミット: `docs: record baseline verify FAIL counts for #347`

---

### Task 2: 設計 — 修正方針の設計書作成とユーザー確認
**前提調査（設計前に事実確認）:**
- [ ] Excel の `2.チェックリスト` シートで `ws.merged_cells.ranges` を全列挙し、タイトル列（C 列）のマージ範囲を特定する
- [ ] `openpyxl` の `MergedCellRange` API を確認し、行マージ検出の方法を empirically 確認する
- [ ] 現在の `_build_p1_sections` の section 生成ロジックを正確に把握する

**設計:**
- [ ] 修正アプローチを決定する（TDD: グループ化 or フォワードフィル）
  - Software Engineer expert review を subagent で実施し、設計を評価する
- [ ] `tools/rbkc/docs/rbkc-converter-design.md` §8 に新挙動の仕様を追記する
- [ ] `tools/rbkc/docs/xlsx-sheet-mapping.md` の `2.チェックリスト` 行に注記を追加する
- [ ] `tools/rbkc/docs/rbkc-verify-quality-design.md` への影響を確認し、必要なら更新する

**⚠️ ユーザー確認が必要 — 設計書更新後にPRでユーザーに確認を求める**
- [ ] コミット: `docs: design for merged-row P1 grouping in security checklist (#347)`

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
