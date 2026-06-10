# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-10 (session 4)

## In Progress

### Task 14: 実験C — 条件M（独立2経路マージ）検証

**Status**: 完了。実験結果はTask 15サマリーに転記済み。

**Steps:**
- [x] 条件M semantic-search.md 作成 (`.tmp/experiment-m/workflows/semantic-search.md`)
- [x] 実験用 skill_dir セットアップ (.tmp/experiment-m/)
- [x] 動作確認: pre-01 で1回実行し結果確認 (20260610-151632/)
- [x] 条件M: qa-05 × 3回 実行 (20260610-151935/, 20260610-151955/, 20260610-152553/)
- [x] 条件0: qa-05 × 3回 実行 (既存結果 20260610-143114/143341/143552/ を使用)
- [x] 条件M: 回帰シナリオ (qa-02/review-07/impact-03: 20260610-152837/, qa-11a: 20260610-153938/)
- [x] 結果集計・表作成 — committed `5ac667383`
- [x] tasks.md 更新・コミット — committed `02bebca53`

### Task 15: 実験D — 条件20（関門1: 両経路20件）検証

**Status**: 実験完了、結果集計済み。

**実験設計**:
- 目的: 関門1（adapterページが候補集合に含まれるか）の安定性のみを測定
- 条件20: index経路20件 + classes経路20件 独立選択 → dedup マージ
- Step 3以降（セクション読み取り・回答生成）は省略（コスト削減）
- 評価: qa-05 × 10回、各回 selected_pages に adapter 含有するか Yes/No

**実験資産**:
- 条件20 semantic-search.md: `.tmp/experiment-20/workflows/semantic-search.md`
- 実験用 skill_dir: `.tmp/experiment-20/` (knowledge/scripts は nabledge-6 へ symlink)
- ランナー: `tools/benchmark/scripts/run_page_selection.py`
- プロンプト: `tools/benchmark/prompts/page-selection-only-prompt.md`
- 結果: `tools/benchmark/results/20260610-163050/`

**実験結果（条件20, qa-05 × 10回）**:
| 試行 | 候補総数 | adapter含有 | 順位 |
|------|----------|------------|------|
|  1 | 22 | Yes | 11 |
|  2 | 26 | Yes | 15 |
|  3 | 26 | Yes |  6 |
|  4 | 16 | Yes | 10 |
|  5 | 23 | Yes | 12 |
|  6 | 18 | Yes | 10 |
|  7 | 22 | Yes | 13 |
|  8 | 21 | Yes | 12 |
|  9 | 15 | Yes |  6 |
| 10 | 21 | Yes | 13 |

**結果**: 10/10 回 adapter 含有

**Steps:**
- [x] 条件20 semantic-search.md 作成 (`.tmp/experiment-20/workflows/semantic-search.md`)
- [x] 実験用 skill_dir セットアップ (.tmp/experiment-20/)
- [x] run_page_selection.py ランナー作成
- [x] 動作確認: trials=1 で動作確認 (.tmp/experiment-20-pre/)
- [x] 本番: qa-05 × 10回 実行 (20260610-163050/)
- [x] 結果集計・表作成（会話内で出力済み）
- [x] [DECISION: ユーザーが次の打ち手を決定 → 条件S（3段階判定）実験を実施]
- [x] tasks.md 更新・コミット — committed `fd3dbc052`
- [x] 実験資産・結果 コミット — committed `fd3dbc052`



## Rules

- 1コミット = 1タスク
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- SCを満たすようタスクを分割し、タスクリストを作業記録に出力する
- タスクリストをコミットし、PRを作成する
- PR上でIssueの目的とタスクリストの対応関係を示し、ユーザーに確認を依頼する
- 承認後、1コミット = 1タスクで各タスクを実装する
- RBKCのcreate/verifyを変更するため: 実装前に設計を行い、設計書・verify設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## Done

- [x] Task 0: タスクリスト作成・PR作成・ユーザー確認 — committed `5ff81b145`
- [x] Task 1: 設計書更新 (classes-md-spec.md, rbkc-verify-quality-design.md QO5) — committed `0dd249d45`
- [x] Task 2: TDD — test_classes.py 作成 (RED) — committed `ac7f7a1f8`
- [x] Task 3: TDD — TestCheckClassesCoverage を test_verify.py に追加 (RED) — committed `4c04146f5`
- [x] Task 4: 実装 — classes.py (generate_classes_md) — committed `fc35cabf4`
- [x] Task 5: 実装 — verify.py (check_classes_coverage) — committed `b1ab38c53`
- [x] Task 6: run.py 統合 (generate_classes_md + check_classes_coverage) — committed `e3da286b8`
- [x] Task 7: v6 classes.md 生成、FAIL 0 確認 — committed `40d313761`
- [x] Task 8: semantic-search.md パッチ1〜3 全5バージョン適用 — committed `f75480b40`
- [x] Task 10: 全バージョン RBKC 展開 (v5/v1.4/v1.3/v1.2) FAIL 0 確認 — committed `d89204139`
- [x] Task 9: ベンチマーク実行 — 全33シナリオ 95.8% (regression なし) — committed `0f702f7ba`
- [x] Task 11: ベンチマーク詳細分析 + qa-11a 5回再実行 (5/5=1.0、単発ブレ確定) — committed `ce20c5dac`
- [x] PR #369 body 更新 (benchmark-results.md リンク + SC最終状態)
- [x] Task 12: ベンチマーク再実行 (HOW-TO-RUN 手順通り) + qa-05 根本原因調査 — committed `e4ca8a50c`
- [x] Task 13: 実験A（classes.md索引比較）+ 実験B（ページ上限40）— committed `5ac667383`
- [x] Task 14: 実験C — 条件M（独立2経路マージ）qa-05×3 + 回帰4本 — committed `5ac667383`
- [x] Task 15: 実験D — 条件20（関門1: 両経路20件）qa-05×10 → 10/10 adapter含有 — committed `fd3dbc052`
- [x] Task 16: 実験E — 条件S（3段階判定）qa-05×10 → 2/10 adapter含有 — committed `84edd9cc7`
- [x] Task 17: 実験F — 条件5step（両経路20件マージ）qa-05×10 + 他4シナリオ × 各1回 — committed `TBD`
