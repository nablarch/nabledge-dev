# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-10

## In Progress

### Task 13: qa-05 設計見直し — 検証実験2本完了、次の方針決定待ち

**Status**: 実験A（classes.md索引比較 9試行）・実験B（ページ上限40+全セクション 7試行）完了。
semantic-search.md は origin/main に戻し済み（committed `22b22b765`）。
classes.md資産・RBKCコードは保持。設計方針の次ステップをユーザーが決定待ち。

**実験A結果（classes.md索引比較、9試行）**:
- 条件A (index.md のみ): adapters-jaxrs-adaptor 選択 2/3（9位, 9位）
- 条件B (classes.md のみ): adapters-jaxrs-adaptor 選択 3/3（9位, 7位, 9位）
- 条件C (両方): adapters-jaxrs-adaptor 選択 **0/3**（10枠をindex系ページが占領）
- 結論事実: index+classes 一括マージ・一括トリムは悪化させる

**実験B結果（ページ上限40+全セクション、qa-05×3＋回帰4本）**:
- qa-05: correctness 0.6/0.6/0.6、adapter選択 **0/3**（条件0も 0.6/0.6/1.0）
- 回帰4本（qa-02, qa-11a, review-07, impact-03）: 全1.0変化なし
- コスト: 条件40-all 平均 $0.612（条件0平均 $0.849 の **0.72x**）
- 結論事実: ページ上限を40に上げても同じindex系ページが選ばれ続け、adapter到達ゼロ

**実験結果dir (未コミット)**:
- `tools/benchmark/results/20260610-143114/` (qa-05 trial-1)
- `tools/benchmark/results/20260610-143341/` (qa-05 trial-2)
- `tools/benchmark/results/20260610-143552/` (qa-05 trial-3)
- `tools/benchmark/results/20260610-143806/` (回帰シナリオ)

**Steps:**
- [x] 実験A: classes.md索引比較 9試行（9サブエージェント）
- [x] 実験B: ページ上限40+全セクション 7実行（qa-05×3 + 回帰4本）
- [x] semantic-search.md を origin/main に revert — committed `22b22b765`
- [x] DECISION: ユーザーが方針 (a) 「独立2経路マージ」を選択 → Task 14で実験

### Task 14: 実験C — 条件M（独立2経路マージ）検証

**Status**: 実験準備中。.tmp/experiment-m/ に条件M用 semantic-search.md を作成済み。

**実験設計**:
- 条件M: index経路(N=8) + classes経路(M=4) を独立に完走させ、classes経路優先でマージ
- 条件0: 現状ベースライン（nabledge-6 そのまま）
- 評価対象: qa-05 × 3回 ずつ
- 追加検証: 条件M で qa-02/qa-11a/review-07/impact-03 各1回

**実験資産**:
- 条件M semantic-search.md: `.tmp/experiment-m/workflows/semantic-search.md`
- 実験用 skill_dir: `.tmp/experiment-m/` (knowledge/等は nabledge-6 へ symlink)

**Steps:**
- [x] 条件M semantic-search.md 作成 (`.tmp/experiment-m/workflows/semantic-search.md`)
- [x] 実験用 skill_dir セットアップ (.tmp/experiment-m/)
- [x] 動作確認: pre-01 で1回実行し結果確認 (20260610-151632/)
- [x] 条件M: qa-05 × 3回 実行 (20260610-151935/, 20260610-151955/, 20260610-152553/)
- [x] 条件0: qa-05 × 3回 実行 (既存結果 20260610-143114/143341/143552/ を使用)
- [x] 条件M: 回帰シナリオ (qa-02/review-07/impact-03: 20260610-152837/, qa-11a: 20260610-153938/)
- [x] 結果集計・表作成 (会話内で出力済み)
- [ ] tasks.md 更新・コミット
- [ ] 実験結果 benchmark/results/ コミット (条件M全試行 + 回帰)

**実験結果サマリー（条件M vs 条件0）**:

qa-05 (各3回):
| 条件 | 試行 | correctness | adapter選択 | adapter順位 | adapterセクション到達 |
|------|------|-------------|------------|------------|----------------------|
| M | trial-1-retry (152553) | 0.6 | No | — | No |
| M | trial-2 (151935) | 1.0 | Yes | 6位 | No（枠外） |
| M | trial-3 (151955) | 0.6 | Yes | 3位 | Yes (s2) |
| 0 | trial-1 (143114) | 0.6 | No | — | No |
| 0 | trial-2 (143341) | 0.6 | No | — | No |
| 0 | trial-3 (143552) | 0.6 | No | — | No |

回帰 (各1回):
| シナリオ | 条件0 SC | 条件M SC | コスト比 |
|---------|---------|---------|--------|
| qa-02 | 1.0 | 1.0 | 0.88x |
| qa-11a | 1.0 | 1.0 | 0.48x |
| review-07 | 1.0 | 1.0 | 0.91x |
| impact-03 | 1.0 | 1.0 | 1.50x |

次の判断: ユーザーが結果を見て設計方針を決定（結論はユーザー側）

### Task 12: ベンチマーク再実行 (HOW-TO-RUN 手順通り 3 run) + qa-05 設計見直し判断

**Status**: 完了済み（実験結果はTask 13に移管）。

**Steps:**
- [x] フェーズ0: results 整理 (旧軸削除・DeepEval baseline リネーム) — committed `565f2fc49`
- [x] run-1 実行 (33/33 正常、qa-06 単体再実行で回収) — committed `10f1ae256`
- [x] qa-05 根本原因調査 (classes.md 非発動の機序・baseline 比較・単体3回実行確認) — committed `e4ca8a50c`


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
