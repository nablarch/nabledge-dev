# Tasks: Replace LLM judge with DeepEval RAG metrics in QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-05-28 (T17完了)

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## In Progress

### ~~T12: docs/benchmark-design.md 更新~~ — committed `4682e518`

**目的**: 設計書をDeepEval完全置き換えの方針に合わせて書き直す。

**変更内容**（grepで確認済みの箇所）:
- 評価軸の表: C-claim/ハルシネーション行を削除、DeepEval3指標の行に置き換え
- 評価ロジック: LLMジャッジの実装詳細（c-claim-judge/hallucination-judge）をDeepEvalの説明に置き換え
- スコア計算: PRESENT/ABSENT/UNCERTAIN → DeepEval数値スコア（0.0〜1.0）に変更
- 設計意図: 「FAILは人間が最終判断」→「閾値で自動判定」に変更
- UNCERTAIN扱いの節: 削除
- DeepEval追加の背景: 「並走」→「置き換え」に変更、相関分析は完了済み（96.4%/88.5%一致）として記述
- ディレクトリ構造: `c-claim-judge.md` / `hallucination-judge.md` の参照を削除
- 「既存指標との相関確認まで...」の注記を削除

**受入条件**: benchmark-design.md にLLMジャッジの記述が残っていない

**コミット**: `docs: rewrite benchmark-design.md for DeepEval replacement`

---

### T13: tools/benchmark/HOW-TO-RUN.md 更新

**目的**: 手順書をDeepEval完全置き換え後のベストプラクティスに合わせて書き直す。

**変更内容**（grepで確認済みの箇所）:
- 出力ファイル早見表: `evaluation.json` の説明を「DeepEval3指標（answer_correctness/answer_relevancy/faithfulness）」に更新、`--with-deepeval` の記述を削除
- ステップ1/2のコマンド: `--with-deepeval` フラグを削除（常時計算のため不要）
- ステップ3「妥当性評価（AIが判断 → ユーザーが承認 → FAILが確定）」を全面書き直し:
  - 新: 「スコア確認」— レポートの閾値割れシナリオを一覧する
  - 承認ループ・確定FAILの概念を削除
  - PRESENT/ABSENT/UNCERTAIN の説明を削除
- ステップ4: 「確定FAIL一覧」→「閾値割れシナリオ一覧」に変更
- ステップ5: 「確定FAILの根本原因調査（AIが判断 → ユーザーが承認）」→「閾値割れシナリオの改善判断」に変更

**受入条件**: HOW-TO-RUN.md にLLMジャッジ・UNCERTAINの記述が残っていない

**コミット**: `docs: rewrite HOW-TO-RUN.md for DeepEval replacement`

---

### T14: テスト更新（RED）

**目的**: 削除するコードのテストを先に除去し、置き換え後の期待動作をテストで明確にする。

**削除するテスト**（test_evaluate.py）:
- `TestCalculateAccuracyScore` クラス全体
- `TestCalculateHallucinationScore` クラス全体
- `TestDetermineHumanReviewItems` クラス全体
- `TestBuildCClaimPrompt` クラス全体
- `TestBuildHallucinationPrompt` クラス全体
- `TestParseHallucinationResponse` クラス全体
- `TestEvaluateScenario` 内の accuracy/hallucination 関連アサーション
- `evaluate` インポートから `build_hallucination_prompt`, `calculate_accuracy_score` 等を削除

**削除するテスト**（test_report.py）:
- `_make_evaluation` の `claim_verdicts`/`hallucination`/`accuracy`/`hallucination_score` パラメータ
- accuracy/hallucination 列に関するアサーション
- `TestFormatHumanReviewList` クラス全体

**更新するテスト**（test_run_qa.py）:
- `FAKE_EVAL` の `accuracy`/`hallucination` キーを削除

**新規追加テスト**:
- `evaluate_scenario` が LLM を呼ばず DeepEval 3指標のみ返すことを確認するテスト

**受入条件**: テストがREDになる（削除予定コードがまだあるためFAIL）

**コミット**: `test: update tests for DeepEval-only evaluation`

---

### T15: evaluate.py 実装変更（GREEN）

**目的**: LLMジャッジを削除し、DeepEvalを常時計算に変更する。

**削除する関数**:
- `calculate_accuracy_score`
- `calculate_hallucination_score`
- `determine_human_review_items`
- `build_c_claim_prompt`
- `build_hallucination_prompt`
- `parse_hallucination_response`

**`evaluate_scenario` の変更**:
- claim-judge / hallucination-judge の呼び出しをすべて削除
- `section_loader` / `page_loader` は `build_deepeval_test_case` で使用するので残す
- `with_deepeval` / `deepeval_model` パラメータを削除（常時計算）
- `scores` の構造を変更: `{"answer_correctness": {"score": 0.9, "reason": "..."}, ...}` 形式にする（調査のためreasonを保持）
- `claim_verdicts` / `hallucination` / `needs_human_review` / `human_review_items` フィールドを返却から削除
- `diagnostics` フィールドを返却から削除（`workflow_details.json` の step3 と完全重複）
- `metrics` フィールドを返却から削除（`metrics.json` と完全重複）

**`_run_deepeval_metric` の変更**:
- `score` だけでなく `reason` も返すよう変更: `return {"score": metric.score, "reason": metric.reason}`

**`evaluate_all` の変更**:
- `llm_fn` パラメータを削除

**受入条件**: 全テスト PASS

**コミット**: `feat: remove LLM judges from evaluate.py, use DeepEval only`

---

### T16: report.py 実装変更

**目的**: accuracy/hallucination 列を削除し DeepEval3指標のみのレポートにする。

**scoresの構造変更への対応**:
- `scores.answer_correctness` が `float` → `{"score": float, "reason": str}` に変わるため読み取り箇所を更新
- `metrics` を `evaluation.json` ではなく `metrics.json` から読むよう変更

**変更内容**:
- `format_scenario_report`: accuracy/hallucination 節を削除、DeepEvalのreasonを表示
- `format_summary`: accuracy/hallucination 集計行を削除、DeepEvalサマリーのみ残す
- `_avg_accuracy` / `_hallucination_pass` 関数を削除
- compare機能: accuracy/hallucination 比較列を削除、DeepEval指標の比較に置き換え
- `format_human_review_list` 関数を削除
- metricsの読み取りを `metrics.json` から行うよう変更

**受入条件**: 全テスト PASS

**コミット**: `feat: remove LLM judge columns from report.py`

---

### T17: run_qa.py から --with-deepeval フラグ削除

**変更内容**:
- `--with-deepeval` 引数を削除
- `run_qa_all` の `with_deepeval` パラメータを削除
- `evaluate_scenario` 呼び出しから `with_deepeval=` を削除

**受入条件**: 全テスト PASS

**コミット**: `feat: remove --with-deepeval flag, DeepEval always runs`

---

### T18: 動作確認（1件実行）

**作業**:
- `python3 -m tools.benchmark.scripts.run_qa --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --scenario-ids pre-01` を実行
- `evaluation.json` に `answer_correctness`/`answer_relevancy`/`faithfulness` があり `accuracy`/`hallucination` がないことを確認
- `report.md` にDeepEval3指標が表示され accuracy/hallucination 列がないことを確認

**コミット**: なし（動作確認タスク）

---

### T19: QAベンチマーク全件実行・新ベースライン取得（3 run）

**目的**: 評価ロジックがDeepEvalに置き換わったため、旧ベースライン（accuracy/hallucination）は無効。新しいベースラインを取得する。

**注意**:
- キーワード検索ベンチマークはLLMジャッジ未使用のため取り直し不要
- 既存の `baseline-current/` は旧指標のものなので上書きしない。新ディレクトリに保存する

**作業**:
- 全30シナリオを3 run実行: `tools/benchmark/results/baseline-deepeval/run-1〜3/`
- `report.py --compare` で3 run集計
- `baseline-current/` の代替として `baseline-deepeval/` を新ベースラインとして記録
- 結果を `.work/00361/notes.md` に追記

**受入条件**: 3 run全て正常完了、DeepEval3指標のレポートが出力される

**コミット**: `chore: save baseline-deepeval QA benchmark results (3 runs)`

---

### T20: 変更差分チェック + diff-check.md 更新

**コミット**: `docs: update diff check for LLM judge removal`

---

## Done

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
