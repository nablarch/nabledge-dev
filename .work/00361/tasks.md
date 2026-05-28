# Tasks: Add standard RAG metrics (DeepEval) to QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-05-28

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## In Progress

---

## Not Started

### T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング

**目的**: 実装前に2点を事実確認する。

1. **ジャッジLLM接続方式**: DeepEvalの各指標はLLM-as-judgeで動く。DeepEval標準の`deepeval.anthropic.Anthropic`は`ANTHROPIC_API_KEY`（Anthropic直接接続）を要求するが、本環境はAWS Bedrock経由（`jp.anthropic.claude-sonnet-4-6`）で`ANTHROPIC_API_KEY`を持たない。以下3択のどれが現実的かを調べる:
   - **案A**: DeepEvalのカスタムモデルAPIに`langchain-aws`のBedrock wrapperを渡す
   - **案B**: DeepEvalのカスタムモデルAPIに既存の`claude CLI`サブプロセス方式をラップして渡す
   - **案C**: DeepEvalのスコア計算ロジックだけ参考に自前実装（DeepEval不使用）
2. **LLMTestCaseへのマッピング**: DeepEvalは`LLMTestCase(input, actual_output, expected_output, retrieval_context)`を要求する。既存データからのマッピングを確認する。
   - `input` ← `scenario["when"]["input"]`
   - `actual_output` ← `answer.md`
   - `expected_output` ← `must.facts`を改行結合したテキスト（Answer Correctness/Similarity用）
   - `retrieval_context` ← `workflow_details.step3.selected_pages`の各ページ内容リスト（Faithfulness用）

**作業**:
- `uv pip install deepeval` を `~/venv` に試行して成功を確認
- DeepEvalのカスタムモデルAPI（`DeepEvalBaseLLM`）仕様を調べ、案A/B/Cの実現可否を確認
- 採用する接続方式を1つ選んで根拠とともに `.work/00361/notes.md` に記録

**コミット**: なし（調査タスク）

---

### T2: tools/benchmark/requirements.txt 新設 + setup.sh にインストールステップ追加

**目的**: DeepEval を benchmark 専用の依存として管理し、setup.sh から自動インストールできるようにする。

**影響ファイル**:
- `tools/benchmark/requirements.txt`（新規作成）
- `setup.sh`（L206-234 付近に benchmark 依存のインストールブロックを追加）

**作業**:
- `tools/benchmark/requirements.txt` を作成し `deepeval` を記載
- `setup.sh` に以下を追加（tools/rbkc/requirements.txt インストールブロックの直後）:
  ```bash
  if [ -f "tools/benchmark/requirements.txt" ]; then
      print_status info "Installing benchmark dependencies..."
      if uv pip install --python "$VENV_DIR/bin/python" -r tools/benchmark/requirements.txt; then
          print_status ok "Benchmark dependencies installed"
      else
          print_status error "Failed to install benchmark dependencies"
          exit 1
      fi
  fi
  ```
- setup.sh の検証ブロック（L220-234付近）に `import deepeval` の確認を追加

**受入条件**: `uv pip install -r tools/benchmark/requirements.txt` が exit 0

**コミット**: `chore: add benchmark requirements.txt and setup.sh install step`

---

### T3: テスト追加（RED） — DeepEval 3指標計算のunit test

**目的**: TDD先行。実装前にテストを書いてREDを確認する。

**影響ファイル**:
- `tools/benchmark/tests/test_evaluate.py`

**作業**:
- T1で確認したLLMTestCaseマッピングをもとに以下のテストクラスを追加:
  - `TestBuildDeepEvalTestCase`: シナリオ + runner_output → `LLMTestCase` のマッピング検証
  - `TestComputeDeepEvalMetrics`: モックで3指標（answer_correctness, answer_similarity, faithfulness）の計算結果を検証
  - `TestEvaluateScenarioWithDeepEval`: `evaluate_scenario` の戻り値に `scores.answer_correctness` 等が含まれることを検証

**受入条件**: `pytest tools/benchmark/tests/test_evaluate.py` が新規テストのみ FAIL（既存テストは全てPASS）

**コミット**: `test: add DeepEval metric computation tests (RED)`

---

### T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加

**目的**: T3のテストをGREENにする。

**影響ファイル**:
- `tools/benchmark/scripts/evaluate.py`

**作業**:
- `build_deepeval_test_case(scenario, runner_output, knowledge_dir, page_loader)` 関数を追加
  - `retrieval_context` は `workflow_details.step3.selected_pages` の各ページ内容リスト
  - `expected_output` は `must.facts` を改行結合したテキスト
- `compute_deepeval_metrics(test_case)` 関数を追加
  - `AnswerCorrectnessMetric`, `AnswerSimilarityMetric` (or GEval), `FaithfulnessMetric` を計算
  - 戻り値: `{"answer_correctness": float, "answer_similarity": float, "faithfulness": float}`
- T1の認証方式確認結果に従ってモデル設定を実装
- `evaluate_scenario` の `scores` フィールドに3指標を追加
- `evaluate_all` で `compute_deepeval_metrics` を呼び出すかどうか（`--with-deepeval` フラグで制御）

**受入条件**: `pytest tools/benchmark/tests/test_evaluate.py` が全てPASS

**コミット**: `feat: add DeepEval metric computation to evaluate.py`

---

### T5: report.py — レポートにDeepEval指標列を追加

**目的**: SC3対応。レポートで標準指標スコアを既存LLMジャッジスコアと並べて表示する。

**影響ファイル**:
- `tools/benchmark/scripts/report.py`
- `tools/benchmark/tests/test_report.py`

**作業**:
- `format_scenario_report`: 評価結果テーブルに `answer_correctness`, `answer_similarity`, `faithfulness` 列を追加
  - `scores` に DeepEval指標がない場合は `N/A` 表示（後方互換）
- `format_summary_report`: サマリーテーブルに3指標の平均を追加
- `format_comparison_report`: 比較レポートに3指標の差分を追加
- テスト: `test_report.py` に DeepEval指標あり/なしの両ケースを追加

**受入条件**: `pytest tools/benchmark/tests/test_report.py` が全てPASS

**コミット**: `feat: add DeepEval metric columns to benchmark report`

---

### T6: docs/benchmark-design.md — DeepEval指標設計追記

**目的**: SC4対応。指標選定根拠とPASS/FAILしきい値を文書化する。

**影響ファイル**:
- `docs/benchmark-design.md`

**作業**:
- 既存の評価ロジック説明セクションの後に「標準RAGメトリクス（DeepEval）」セクションを追加:
  - 指標選定根拠（なぜこの3指標か、既存LLMジャッジとの関係）
  - 各指標の定義と入力マッピング（シナリオデータ → LLMTestCase）
  - PASS/FAILしきい値の設計根拠（T1/T4の結果を踏まえて設定）
  - 既存LLMジャッジとの並走方針（置き換えか補完か）

**受入条件**: ドキュメントに指標選定根拠・しきい値が明記されている

**コミット**: `docs: add DeepEval metrics design to benchmark-design.md`

---

### T7: 動作確認（1件実行）

**目的**: DeepEval統合が基本動作することを最小コストで確認する。

**作業**:
- `python3 -m tools.benchmark.scripts.run_qa --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --scenario-ids pre-01 --with-deepeval` を実行
- `evaluation.json` に `scores.answer_correctness`, `scores.answer_similarity`, `scores.faithfulness` が含まれることを確認
- `report.md` に3指標が表示されることを確認

**受入条件**: pre-01 の evaluation.json にDeepEval 3指標が出力される、エラーなし

**コミット**: なし（動作確認タスク）

---

### T8: 動作確認（3件実行）

**目的**: 複数シナリオで安定動作することを確認する。

**作業**:
- `pre-01`, `pre-02`, `qa-01` の3件を実行
- 3件とも evaluation.json に DeepEval 3指標が含まれることを確認
- レポートのサマリーテーブルに3指標の集計が出ることを確認

**受入条件**: 3件全て正常完了、レポートに3指標集計あり

**コミット**: なし（動作確認タスク）

---

### T9: 全件実行 + 相関分析（SC1・SC2）

**目的**: 全30シナリオでDeepEval指標を取得し、既存LLMジャッジとの相関・不一致ケースを文書化する。

**注意**: 既存の `tools/benchmark/results/baseline-current/` には一切触れない。新規の run ディレクトリに結果を保存する。

**作業**:
- 全シナリオを `--with-deepeval` で実行し、`tools/benchmark/results/deepeval-validation/run-1/` に保存
- 相関分析: 各シナリオの `accuracy`（既存）と `answer_correctness`（DeepEval）、`hallucination`（既存）と `faithfulness`（DeepEval）の一致率を計算
- 不一致ケース（既存PASS→DeepEvalFAIL、またはその逆）を列挙して原因を分析
- 結果を `.work/00361/deepeval-validation.md` に記録

**受入条件**: 30シナリオ全て完了、不一致ケースが文書化される

**コミット**: `docs: add DeepEval validation results (SC2)`

---

### T10: HOW-TO-RUN.md 更新

**目的**: DeepEval追加後も手順書通りにベンチマークが実行できることを保証する。

**影響ファイル**:
- `tools/benchmark/HOW-TO-RUN.md`

**作業**:
- 前提セクションに `deepeval` のインストール確認手順を追加
- ステップ1〜2の実行コマンドに `--with-deepeval` フラグの説明を追加
- 出力ファイル早見表に DeepEval 3指標列の説明を追記
- T7/T8の動作確認手順通りに実際に実行して、手順書との齟齬がないことを確認

**受入条件**: HOW-TO-RUN.md の手順通りに実行して `--with-deepeval` フラグ付きで正常完了する

**コミット**: `docs: update HOW-TO-RUN.md for DeepEval integration`

---

### T11: 変更差分チェック

**目的**: PRレビュー依頼前に変更差分が想定した変更のみかを確認する。

**作業**:
- `git diff main...HEAD --stat` で変更ファイル一覧を確認
- 各変更ファイルについて「想定した変更か」を1行ずつ確認
- 意図しない変更（自動生成ファイル、無関係なファイル）がないかチェック
- 結果を `.work/00361/diff-check.md` に記録

**コミット**: `docs: add diff check results`

---

## Done

---

## SCとタスクの対応

| Success Criteria | 対応タスク |
|---|---|
| SC1: 3指標を各シナリオで計算しレポートに含める | T3, T4, T5 |
| SC2: 現行LLMジャッジとの相関・不一致ケース文書化 | T9 |
| SC3: レポートに標準指標スコアを表示 | T5 |
| SC4: 指標選定根拠とPASS/FAILしきい値をbenchmark-design.mdに記載 | T6 |
| SC5: 既存ベンチマークテストが全てPASS | T3, T4, T5（各タスクで既存テストのPASS確認） |
