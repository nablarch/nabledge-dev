# Tasks: Replace LLM judge with DeepEval RAG metrics in QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-06-01

## ルール（今日の追加事項）
- `.claude/settings.json` に `DEEPEVAL_TELEMETRY_OPT_OUT=true` を追加済み（Apache 2.0ライセンス、オプトアウト許可）

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## In Progress

### T20: 変更差分チェック + diff-check.md 更新

**コミット**: `docs: update diff check for LLM judge removal`

---

## Not Started

### T22（完了後）: スキルの挙動問題シナリオの改善（別issue検討）

13件のスキルの挙動問題は別issueで対応する。

---

## Archived In Progress

### T22: ベンチマーク再取得（3 run）— 完了

**背景**: T21の修正後、クリーンな状態でベースラインを再取得する。

**作業**:
- [x] run-1実行 → `baseline-deepeval/run-1/run/` に保存（29/30、qa-11aタイムアウト）
- [x] run-2実行 → `baseline-deepeval/run-2/run/` に保存（26/30、3タイムアウト + oos-qa-01エラー）
- [x] run-1/2のエラーシナリオを単体再実行して上書き
  - run-1: qa-11a → OK
  - run-2: review-07, qa-02, qa-06, oos-qa-01 → 全OK
- [x] run-3実行 → `baseline-deepeval/run-3/run/` に保存（30/30、エラーなし）
  - 中断データ（26シナリオ）+ 残り4シナリオ再実行 + エラー3件（qa-11a/review-06/review-09）再実行済み
- [x] 各run後に `report.py` でレポート生成
- [x] 3 run集計（ステップ4a）
  - answer_correctness: 平均 0.98（run-1: 0.99 / run-2: 0.98 / run-3: 0.98）
  - answer_relevancy:   平均 0.98（run-1: 0.98 / run-2: 0.97 / run-3: 0.98）
  - faithfulness:       平均 0.99（run-1: 0.98 / run-2: 0.98 / run-3: 1.00）
- [x] 閾値割れシナリオの改善判断（ステップ5）
  - 23シナリオで1回以上閾値割れ
  - スキルの挙動問題: 13件（impact-03/impact-06/pre-01/pre-03/qa-01/qa-04/qa-05/qa-12b/qa-13/review-06/review-07/review-09）
  - 揺らぎ（1/3のみ）: 9件 → 対処不要
  - 評価基準の問題: 1件（qa-12a、must.facts修正候補）

**コミット**: `chore: save baseline-deepeval QA benchmark results (3 runs)`

**中間データの場所**:
- run-1: `tools/benchmark/results/baseline-deepeval/run-1/run/`（gitトラック済み？いいえ、untracked）
- run-2: `tools/benchmark/results/baseline-deepeval/run-2/run/`（untracked）
- run-3中断: `tools/benchmark/results/20260529-150210/`（untracked）


## Done

- [x] T22: ベンチマーク再取得（3 run）— committed `42f7e5edd`

- [x] T21: e2e-prompt.md / run_qa.py 修正（Answerマーカー導入） — committed `6c5213430`
- [x] T19: QAベンチマーク全件実行・新ベースライン取得（3 run） — 30/30全件、全指標0.96〜0.99（T21修正前のため廃棄）

- [x] T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング — `5530ab20`
- [x] T2: requirements.txt 新設 + setup.sh — `93669a7b`
- [x] T3: テスト追加（RED） — DeepEval 3指標計算のunit test — `1efc394e`
- [x] T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加 — `1c7a6a0e`
- [x] T5: report.py — レポートにDeepEval指標列を追加 — `d87da7de`
- [x] T6: docs/benchmark-design.md — DeepEval指標設計追記 — `93101e85`
- [x] T7: 動作確認（1件実行）・SSL修正 — `77a43974`
- [x] T8: 動作確認（3件実行） — (実行のみ)
- [x] T9: 全件実行 + 相関分析（SC2） — `bbcc37a50`
- [x] T10: HOW-TO-RUN.md更新（T13で上書き予定） — `f6195085c`
- [x] T11: 変更差分チェック（T19で更新予定） — `7d1a0d52d`
- [x] T12: docs/benchmark-design.md 更新 — `4682e518`
- [x] T13: tools/benchmark/HOW-TO-RUN.md 更新 — `03206b0b`
- [x] T14: テスト更新（RED） — `e202bbb9`
- [x] T15: evaluate.py 実装変更（GREEN） — `00bcd0e1`
- [x] T16: report.py 実装変更 — `5513641a`
- [x] T17: run_qa.py から --with-deepeval フラグ削除 — `4d97f74d`
- [x] T18: 動作確認（1件実行）— 実行のみ、コミットなし
