# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-18

## In Progress

### B-1. 現行検索E2Eベースライン取得（一度限り）

`tools/benchmark/HOW-TO-RUN.md` の手順に従う。run-label = `baseline-current`、シナリオ = `qa-current.json`。

- [x] ステップ1（動作確認）
- [x] ステップ2（run-1）— 完了、30シナリオ、精度83.7%、幻覚PASS20%、$18.22
- [x] ステップ3（run-1 レポート） — レポート生成済み（会話中）
- [x] ステップ2〜3（run-2）— 完了、精度86.0%、幻覚PASS16.7%、$20.73
- [ ] ステップ2〜3（run-3）— ユーザー承認済み、実行してよい
- [ ] ステップ4（集計レポート）→ [BLOCKED: run-3完了後]
- [ ] ステップ5（コミット・プッシュ）

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

- [x] B-0. run_e2e.py 再設計（旧結果削除 `338c8c471`、TDD実装 `218a5e051`）— SEレビュー 0 Findings
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
