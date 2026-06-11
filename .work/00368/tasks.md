# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-11 (session 6)

## In Progress

### Task 19: 実験H — exp-purpose-classes 完了。結論待ち。

**Status**: 40実行完了・コミット済み (`327e681f7`)。結論はユーザーが出す。

**実験設計**:
- qa-05（目的=実装したい）と qa-05b（目的=仕組み・動作を理解したい）— 質問文は同一、目的のみ異なる
- 条件N: 現行 semantic-search.md（index経路のみ）+ 現行 qa.md（10 sections）
- 条件C: exp版 semantic-search.md（index+classes 各20件マージ）+ exp版 qa.md（30 sections）
- 各条件 × 2シナリオ × 10回 = 40実行

**集計結果**:
| 条件-シナリオ | correctness平均 | adapter_section率 |
|---|---|---|
| N-qa-05  | 1.000 | 0% |
| N-qa-05b | 0.040 | 10% |
| C-qa-05  | 1.000 | 40% |
| C-qa-05b | 0.070 | 20% |

結果: `tools/benchmark/results/exp-purpose-classes/results.md`

**Steps:**
- [x] qa.json 更新（qa-05 Converter を acceptable に移動、qa-05b 追加）
- [x] 条件C スキルディレクトリ作成（`.tmp/skill-cond-c/`）
- [x] run_qa.py タイムアウト 360s→600s
- [x] 条件N × qa-05 × 10回実行
- [x] 条件N × qa-05b × 10回実行
- [x] 条件C × qa-05 × 10回実行
- [x] 条件C × qa-05b × 10回実行
- [x] 結果集計・results.md 保存・コミット (`327e681f7`)
- [ ] [DECISION: 結論をユーザーが判断する]



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
- [x] Task 17: 実験F — 条件5step（両経路20件マージ）qa-05×10 + 他4シナリオ × 各1回 — committed `6b72072fb`
- [x] Task 18: 実験G — 条件5step v2（e2e経路）qa-05×10 → 2/10 adapter含有（検証ゲート失敗）— committed `f2a004c1e`
- [x] Task 19: 実験H — exp-purpose-classes（条件N/C × qa-05/qa-05b × 10回）— committed `327e681f7`
