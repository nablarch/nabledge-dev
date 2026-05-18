# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-18

## In Progress

### B-0. run_e2e.py 再設計

**目的**: ミスが起きない構造にする。`--mode` 削除、hearing_answerの注入をシナリオファイルで制御、summary.jsonに実行コンテキスト追加。

**完了済み**:
- [x] out-of-scopeシナリオ2件追加（oos-impact-01, oos-qa-01）— `f21c6f039`
- [x] `qa-current.json` 生成（30シナリオ、hearing_answerなし）— `f21c6f039`
- [x] `evaluate.py` out-of-scope対応（section参照なしfactを空文字で評価）— `f21c6f039`
- [x] シナリオ設計（3フェーズ + oos）を benchmark-design.md に追記 — `f21c6f039`

**影響ファイル**:
- `tools/benchmark/scripts/run_e2e.py` — 主要変更対象
- `tools/benchmark/tests/test_run_e2e.py` — テスト更新
- `tools/benchmark/results/` — 旧結果を削除（不正データのため）
- `tools/benchmark/results/baseline-current-report.md` — 削除

**Steps:**
- [ ] 旧成果物を削除してコミット:
  ```bash
  rm -rf tools/benchmark/results/20260515-171300 \
         tools/benchmark/results/20260515-181817 \
         tools/benchmark/results/20260515-194124 \
         tools/benchmark/results/baseline-current-report.md
  git add -A tools/benchmark/results/
  git commit -m "chore: remove invalid baseline results (hearing_answer was injected)"
  git push
  ```
- [ ] TDD: `test_run_e2e.py` を以下の方針で書き直す（RED）
  - `--mode` 引数が存在しないこと
  - `--knowledge-dir` 引数が存在しないこと
  - `--output-dir` 引数が存在しないこと
  - `--timeout` 引数が存在しないこと
  - hearing_answer が `None` の場合プロンプトに注入しないこと
  - hearing_answer が設定されている場合プロンプトに注入すること
  - `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` が含まれること
  - `trace.json` が保存されること（`claude -p --output-format json` の全出力）
  - `pytest tools/benchmark/tests/test_run_e2e.py` が FAIL（実装前なのでFAILが正しい）
- [ ] `run_e2e.py` を書き直す（GREEN）
  - `--mode` / `--knowledge-dir` / `--output-dir` / `--timeout` を削除
  - hearing_answerの注入ロジック: シナリオの `hearing_answer` が非Noneなら注入、Noneなら注入しない（分岐のみ、モードなし）
  - `knowledge_dir = skill_dir / "knowledge"` に固定
  - `output_dir = tools/benchmark/results/YYYYMMDD-HHMMSS/` に固定
  - `timeout = 360` にハードコード
  - `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` を追加
  - `trace.json` を保存（`claude -p` の生JSON出力全体）— QAエキスパートの定性評価用
  - `pytest tools/benchmark/tests/test_run_e2e.py` が PASS
  - `pytest tools/benchmark/tests/` が全PASS
- [ ] SEレビュー（別エージェント）を実施してユーザーに報告、Findingがあれば修正
- [ ] コミット:
  ```bash
  git add tools/benchmark/scripts/run_e2e.py \
          tools/benchmark/tests/test_run_e2e.py
  git commit -m "feat: simplify run_e2e — remove --mode/--output-dir/--knowledge-dir/--timeout, hearing controlled by scenario"
  git push
  ```

## Not Started

### B-1. 現行検索E2Eベースライン取得（一度限り）

B-0完了後に実施。現行スキルは変わらないため再実行不要。取得後はB-2以降の比較基準として固定する。

**Steps:**
- [ ] 1シナリオで動作確認:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-current.json \
    --skill-dir .claude/skills/nabledge-6 \
    --scenario-ids pre-01
  ```
  - 受入条件: 終了コード0、出力ディレクトリ（`tools/benchmark/results/YYYYMMDD-HHMMSS/`）に `pre-01/` が生成され `hearing.json` / `search.json` / `answer.md` / `metrics.json` / `evaluation.json` が揃うこと
  - 受入条件: `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` が含まれること
  - 受入条件: `pre-01/hearing.json` の `status` が `"skipped"` であること（hearing_answerなし → ヒアリングなし）
  - 受入条件: `pre-01/metrics.json` の `model_usage` が `{}` でないこと
- [ ] run-1 実行（全28シナリオ）:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-current.json \
    --skill-dir .claude/skills/nabledge-6
  ```
  - 受入条件: 終了コード0、`summary.json` の `total_scenarios` = 28
  - 出力ディレクトリをメモしておく（例: `tools/benchmark/results/20260518-171300/`）
  - 完了後リネーム:
    ```bash
    mkdir -p tools/benchmark/results/baseline-current
    mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/baseline-current/run-1
    ```
- [ ] run-2 実行（全28シナリオ）:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-current.json \
    --skill-dir .claude/skills/nabledge-6
  ```
  - 完了後リネーム: `mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/baseline-current/run-2`
- [ ] run-3 実行（全28シナリオ）:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-current.json \
    --skill-dir .claude/skills/nabledge-6
  ```
  - 完了後リネーム: `mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/baseline-current/run-3`
- [ ] 3 run全て完了確認:
  ```bash
  for r in 1 2 3; do
    echo "run-$r: $(ls tools/benchmark/results/baseline-current/run-$r/ | wc -l) entries"
    cat tools/benchmark/results/baseline-current/run-$r/summary.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('  total_scenarios:', d['total_scenarios'], '  scenarios_file:', d['scenarios_file'])"
  done
  ```
  - 受入条件: 3 run全て `total_scenarios: 28`、`scenarios_file` が `qa-current.json` であること
- [ ] 結果をコミット:
  ```bash
  git add tools/benchmark/results/baseline-current/
  git commit -m "feat: add baseline-current E2E results (3 runs, no hearing_answer)"
  git push
  ```
- [ ] 集計レポートを生成してユーザーに報告
  - 設計書フォーマット（benchmark-design.md §集計レポート）に従い `.tmp/generate_report.py` で集計
  - 保存先: `tools/benchmark/results/baseline-current/report.md`
  - [BLOCKED: ユーザーが数値を確認し、B-2着手の承認を出す]

### B-2. RBKC変更

B-1完了後に実施。目的: `index.md`（知識ファイル一覧）と `terms.json`（検索語辞書）を生成できる状態にする。

**影響調査結果**:
- `verify.py` は `index.md` と `terms.json` を一切チェックしない（QO4は `index.toon` のみ）
- `tools/benchmark/scripts/generate_index.py` にindex.md生成ロジック実装済み — RBKCへの統合が必要

**作業A: index.md生成をRBKCに統合**

- [ ] 変更前のFAIL数を記録:
  ```bash
  for v in 6 5 1.4 1.3 1.2; do
    echo -n "v$v: "; (cd tools/rbkc && bash rbkc.sh verify $v 2>&1 | grep -c "FAIL") || echo "0"
  done
  ```
- [ ] TDD: `test_index.py` に `generate_index_md()` のテストを追加（RED）
  - `pytest tools/rbkc/tests/ut/test_index.py` が FAIL
- [ ] `index.py` に `generate_index_md()` を実装（GREEN）
  - `pytest tools/rbkc/tests/ut/test_index.py` が PASS
  - `run.py` の create/update/delete で呼び出す
- [ ] 全5バージョンで create+verify:
  ```bash
  for v in 6 5 1.4 1.3 1.2; do
    echo "=== v$v ===" && (cd tools/rbkc && bash rbkc.sh create $v && bash rbkc.sh verify $v) 2>&1 | tail -3
  done
  ```
  - 受入条件: 各バージョンで `index.md` が生成され、FAIL数が変更前と同じ
- [ ] コミット: `feat: add generate_index_md to RBKC`

**作業B: terms.json生成をRBKCに新規実装**

- [ ] TDD: `test_terms.py` を新規作成（RED）
  - `pytest tools/rbkc/tests/ut/test_terms.py` が FAIL
- [ ] `terms.py` を実装（GREEN）
  - `pytest tools/rbkc/tests/ut/test_terms.py` が PASS
  - `run.py` の create/update/delete で呼び出す
- [ ] 全5バージョンで create+verify（同上コマンド）
  - 受入条件: 各バージョンで `terms.json` が生成され、FAIL数が変更前と同じ
- [ ] コミット: `feat: add generate_terms to RBKC`

### B-3. スキルデプロイ

B-2完了後に実施。目的: ベンチマークで検証済みの部品プロンプト・スクリプトをスキルに組み込む。

- [ ] 部品をスキルにコピー:
  ```bash
  diff tools/benchmark/components/prompts/ .claude/skills/nabledge-6/assets/
  diff tools/benchmark/components/scripts/ .claude/skills/nabledge-6/scripts/
  ```
  - 受入条件: 差分がない（ベンチマーク済みと一致）
- [ ] ワークフロー作成（各ファイルをPEレビュー後にコミット）:
  - `qa/hearing.md`, `semantic-search.md`, `keyword-search.md`
  - `qa/answer.md`, `qa/verify.md`, `qa.md`, `code-analysis.md`
- [ ] 1シナリオでスモークテスト:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .claude/skills/nabledge-6 \
    --scenario-ids pre-01
  ```
  - 受入条件: 終了コード0、`pre-01/answer.md` に `参照:` セクションあり、`metrics.json` の `model_usage` が `{}` でない
  - 受入条件: `pre-01/search.json` のセクションIDが現行ベースラインの同シナリオと異なること（新検索が使われていること）

### B-4. 新スキルE2Eベンチマーク

B-3完了後に実施。

- [ ] 1シナリオで動作確認（B-3スモークテストと同じコマンド、今度は評価も確認）:
  - 受入条件: `pre-01/evaluation.json` が生成され `claim_verdicts` が空でないこと
- [ ] run-1 実行（全28シナリオ）:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .claude/skills/nabledge-6
  ```
  - 受入条件: 終了コード0、`total_scenarios` = 28、`summary.json` の `scenarios_file` が `qa.json` であること
  - 完了後リネーム: `mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/v1-new-search/run-1`
- [ ] run-2, run-3 実行（同上、run-2/run-3にリネーム）
- [ ] 結果をコミット
- [ ] QAエキスパート（別エージェント）に生データを渡して比較評価させる（実装者が自己採点しない）
- [ ] [BLOCKED: ユーザーがQAエキスパートの評価を確認し、B-5着手の承認を出す]

### B-5. 改善サイクル

B-4で現行未満の項目がある場合に実施。

- [ ] QAエキスパートの評価から劣化シナリオを特定
- [ ] 劣化原因を部品ベンチマークで特定（`simulate_*.py --scenario-ids <id>`）
- [ ] PE（プロンプト変更）またはSE（スクリプト変更）に改善案を相談してから実装
- [ ] E2Eベンチマーク再実行（`results/v2-new-search/` に保存）
- [ ] QAエキスパートによる再評価
- [ ] 全シナリオで baseline-current 以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後。v6で確定した検索をv5/v1.xに展開。

- [ ] v5: ワークフロー・アセット・スクリプトをコピー（パス置換のみ）
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .claude/skills/nabledge-5 \
    --scenario-ids pre-01
  ```
- [ ] v1.4, v1.3, v1.2: 同上

### B-7. nabledge-test削除

B-6完了後。新ベンチマーク基盤に完全移行。

- [ ] `test-setup.sh` の `_scenario_field` 削除、質問・キーワードをハードコード
  - `bash tools/tests/test-setup.sh` が全バージョンでエラーなく完了
- [ ] `.claude/skills/nabledge-test/` / `.claude/agents/nabledge-test-runner.md` 削除
- [ ] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除
- [ ] `.claude/rules/` からnabledge-test固有記述を削除
- [ ] `python3 -m pytest tools/ -x` で全テストPASS

## Done

- [x] B-1（旧）. 現行検索E2Eベースライン取得（不正データのためB-0でリセット） — `f57b78581`, `4de6fb47b`
- [x] A-1. RBKC変更のリバート — `5bf479e1c`, `f0249fea0`
- [x] A-2. 設計書の整合 — `b3819fb94`
- [x] A-3. 部品プロンプトの移動 — `eea31f065`, `426b9a0f4`
- [x] A-4. read-sections.sh テスト追加 — `b65064dce`
- [x] A-5. 部品スクリプトの移動 — `d2e6db620`, `0724b3faa`
- [x] A-6. マージ — `8d95af52e`

### ベンチマーク基盤（完了済み）

評価エンジン（`evaluate.py`, 54テストGREEN）、ランナー群（`simulate_*.py`, `run.py`）。QAシナリオ28件（`qa.json`）、キーワード検索シナリオ12件（`keyword-search.json`）。SE/QAレビュー済。

### 意味検索（完了済み）

2段階方式（Stage1: カテゴリ選定 → Stage2: セクション選定）。部品ベンチマーク: 97.4%（37/38 must）。ユーザー承認済。

### 回答生成（完了済み）

知識セクションから引用付き回答を生成。部品ベンチマーク: 18/26 Stable PASS, 1 Stable FAIL（既知）, 7 Unstable。PE/SEレビュー済。

### 根拠検証（完了済み）

ハルシネーション検出。部品ベンチマーク: FP率5%, FN率0%。PEレビュー済。

### ヒアリング（完了済み）

事実ベース分類。部品ベンチマーク: 分類100%, 処理方式100%×3回完全一致。PEレビュー済。

### キーワード検索（完了済み）

terms.jsonによるキーワードマッチ（20テストGREEN）。

### 設計書（完了済み）

`design/` に7本: benchmark-design.md（今回更新）, search-design.md, semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md。
