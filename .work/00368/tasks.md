# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-11 (session 5)

## In Progress

### Task 18: 実験G — 条件5step v2（Step番号維持・e2e経路）検証

**Status**: 検証ゲート失敗。設計・実行済みだが、merged_pages が条件20（15〜26件）と乖離（4〜12件）。

**実験設計**:
- semantic-search.md の Step 番号を現行（1=読込, 2=ページ選択, 3=セクション, 4=Javadoc）のまま維持
- Step 1 で index.md + classes.md 両方読む
- Step 2 を「index経路20件 + classes経路20件 + dedupマージ・トリムなし」に拡張
- qa.md: Step 4 の「Maximum 10 sections total」→「Maximum 30 sections total」
- 実験資産: `.tmp/experiment-5step-v2/`
- 結果: `tools/benchmark/results/20260611-09xxxx/` × 10試行

**検証ゲート状況**:
- 試行1: merged=12、adapter含有=Yes → ゲート通過（合格基準に近い）
- 試行2〜10: merged=4〜8、total_seen=9〜13 → 条件20（15〜26）と乖離
- adapter 関門1: 2/10

**失敗原因（調査済み）**:
- e2e 経路（qa.md → semantic-search 連続実行）では、エージェントがページ選定（Step 2）とセクション選定（Step 3）を1コンテキストで連続実行するため、Step 2 段階で adapter を「実装パターンの主題ではない」として skip する（セクション選定を先読みした早期除外）
- 条件20は page-selection-only ランナー（「Step 2cで停止」指示）だったため、ページ選定に集中して広く取れた
- 今回の classes.md を読んだかどうかは e2e の workflow_details.json からは直接判別不能

**Steps:**
- [x] semantic-search.md 作成 (`.tmp/experiment-5step-v2/workflows/semantic-search.md`)
- [x] qa.md 作成 (`.tmp/experiment-5step-v2/workflows/qa.md`) — Step 4: 30 sections
- [x] diff 確認（2ファイルの差分が想定通りであること確認済み）
- [x] 検証ゲート: 1試行実行 → merged=12、adapter含有=Yes（通過）
- [x] 残り9試行実行 → merged 4〜8件で条件20と乖離、検証ゲート失敗
- [x] 失敗原因調査（e2e コンテキスト内でのページ早期絞り込みを確認）
- [ ] [DECISION: 次の打ち手を決定] — 結果未コミット（タイムアウト失敗試行含む未コミットあり)



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
