# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-09

## In Progress

### Task 11: ベンチマーク結果の詳細分析 — PR作成前確認

**Context** (このセッションで実施):

ユーザーから3点の確認要求あり:
1. 27実行マーカー検証表（元中間ディレクトリ削除済み → pr-368/run-1 で代替確認）
2. answer_correctness -5.7pp の中身（ベースラインとのシナリオ別比較 + ページ選択分析）
3. benchmark-results.md の更新とコミット

**確認1 結果**:
元の27実行中間ディレクトリ（20260609-13xxxx〜14xxxx）は削除済みで実物提示不可。
pr-368/run-1 の9対象シナリオ全てで trace.json 内に `<<<WORKFLOW_DETAILS_JSON>>>` / `<<<END_WORKFLOW_DETAILS>>>` が存在し `<details>` タグ不在・workflow_details.json VALID を確認。9/9 OK。

**確認2 結果**:
ベースライン vs PR のシナリオ別 answer_correctness 比較（30件ペア）:
- qa-11a: 1.000 → 0.10 (-0.900)  判定: LLM回答生成の揺らぎ。同セクション(s4)を読んで出力せず。classes.md非起因
- qa-05: 0.733 → 0.60 (-0.133)  判定: pre-existing（ベースラインも run-1/2=0.60）
- qa-12a: 0.800 → 0.70 (-0.100)  判定: ページ選択揺らぎ（libraries-tag.json が excluded に入った）。classes.md 非起因（Step 3b 未発動）
- review-09: 1.000 → 0.90 (-0.100)  判定: 評価器揺らぎ
- 残り26件: 変化なし
PR起因の correctness 低下はゼロ件。

**ユーザーへの未回答質問**:
benchmark-results.md の更新: PR body の Evidence として記録するか、benchmark-results.md に詳細分析を追記するか、どちらかをユーザーに確認中（→ 回答待ち）

**Steps:**
- [x] 確認1: pr-368/run-1 の9シナリオでマーカー存在を直接確認（9/9 OK）
- [x] 確認2: シナリオ別 correctness 比較表作成、ページ選択変化の有無を workflow_details.json で検証
- [DECISION: benchmark-results.md に詳細分析を追記してコミットするか、PR body のみで記録するか] 確認3: benchmark-results.md 更新・コミット

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
