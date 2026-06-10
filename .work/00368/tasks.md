# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-10

## In Progress

### Task 12: ベンチマーク再実行 (HOW-TO-RUN 手順通り 3 run) + qa-05 設計見直し判断

**Status**: run-1 完了・プッシュ済み。qa-05 失敗の根本原因調査完了。ユーザーの設計判断待ち。

**調査結果（事実）**:
- Issue #368 SC「qa-05 passes」は達成されていない
- classes.md Step 3b は qa-05 に一度も発動していない（入力にクラス名 Jackson2BodyConverter が出現しないため）
- qa-05 の 1.0/0.6 は Step 3（index.md 検索）のモデル揺れに依存。3回単体実行で 1/3=1.0、2/3=0.6
- 今回 run-1 の 0.6 原因: adapters-jaxrs-adaptor が 8番目に選ばれたがセクション評価に届かなかった
- benchmark-results.md では「Pre-existing」と記録していたが SC 未達の事実は正確に伝えていなかった

**Steps:**
- [x] フェーズ0: results 整理 (旧軸削除・DeepEval baseline リネーム) — committed `565f2fc49`
- [x] run-1 実行 (33/33 正常、qa-06 単体再実行で回収) — committed `10f1ae256`
- [x] qa-05 根本原因調査 (classes.md 非発動の機序・baseline 比較・単体3回実行確認)
- [DECISION: qa-05 を救う設計を修正するか? 選択肢: (a) Step 3b のマッチ条件を拡張（クラス名だけでなく機能名・概念でもマッチ）、(b) 真因はセクション到達なので adapters-jaxrs-adaptor を index.md で上位に引き上げる別手当、(c) classes.md の守備範囲外として SC を修正する。ユーザー判断必要] → run-2/3 へ進む前に判断待ち


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
