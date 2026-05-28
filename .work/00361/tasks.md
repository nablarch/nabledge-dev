# Tasks: Add standard RAG metrics (DeepEval) to QA benchmark

**PR**: TBD
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

### T1: 調査 — DeepEval 認証方式とLLMTestCase入力マッピングの確認

**目的**: 実装前に2点を事実確認する。

1. **認証方式**: DeepEvalのAnthropicモジュールは`ANTHROPIC_API_KEY`直接接続を要求する。現環境はBedrockベース（`jp.anthropic.claude-sonnet-4-6`）。Bedrock経由で使えるか、あるいは`langchain-aws`経由のwrapが必要かを確認する。
2. **LLMTestCaseへのマッピング**: DeepEvalは`LLMTestCase(input, actual_output, expected_output, retrieval_context)`を要求する。既存データからのマッピングを確認する。
   - `input` ← `scenario["when"]["input"]`
   - `actual_output` ← `answer.md`
   - `expected_output` ← `must.facts`を連結したテキスト（Answer Correctness/Similarity用）
   - `retrieval_context` ← `workflow_details.step3.selected_pages`の各ページ内容（Faithfulness用）

**作業**:
- `uv pip install deepeval` を `~/venv` に試行して成功を確認
- `python3 -c "from deepeval.anthropic import Anthropic"` で import確認
- Bedrock接続可否を確認（`ANTHROPIC_API_KEY`が必要か、Bedrock endpoint対応かを調べる）
- 結果を `.work/00361/notes.md` に記録

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

### T7: SC2検証 — baseline-currentへのDeepEval後計算と相関分析

**目的**: SC2対応。既存30シナリオのbaseline-current結果に対してDeepEval指標を後計算し、現行LLMジャッジとの相関・不一致ケースを文書化する。

**影響ファイル**:
- `.work/00361/deepeval-validation.md`（新規、作業記録）
- `tools/benchmark/results/baseline-current/run-1/*/evaluation.json`（DeepEval指標を追記）

**作業**:
- `python3 -m tools.benchmark.scripts.evaluate --run-dir ... --with-deepeval` で baseline-current/run-1 に対してDeepEval指標を後計算
- 相関分析: 既存の accuracy/hallucination スコアとDeepEval3指標の一致率を計算
- 不一致ケース（既存PASS→DeepEvalFAIL、またはその逆）を列挙して原因を分析
- 結果を `.work/00361/deepeval-validation.md` に記録

**受入条件**: 30シナリオ全てのevaluation.jsonにDeepEval指標が追記される、不一致ケースが文書化される

**コミット**: `docs: add DeepEval validation results against baseline-current`

---

### T8: 変更差分チェック

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
| SC2: 現行LLMジャッジとの相関・不一致ケース文書化 | T7 |
| SC3: レポートに標準指標スコアを表示 | T5 |
| SC4: 指標選定根拠とPASS/FAILしきい値をbenchmark-design.mdに記載 | T6 |
| SC5: 既存ベンチマークテストが全てPASS | T3, T4, T5（各タスクで既存テストのPASS確認） |
