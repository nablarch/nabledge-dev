# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-19 (B-2作業B再設計: verify設計書更新→TDD→実装の順に変更)

## In Progress

### B-2. RBKC変更

B-1完了後に実施。目的: `index.md`（知識ファイル一覧）と `terms.json`（検索語辞書）を生成できる状態にする。

**作業A: index.md生成をRBKCに統合**

- [x] 変更前のFAIL数を記録: 全バージョン FAIL 0
- [x] TDD: `test_index.py` に `generate_index_md()` のテストを追加（RED）
- [x] `index.py` に `generate_index_md()` を実装（GREEN） — 19テストPASS
- [x] 全5バージョンで create+verify: 全バージョン All files verified OK、FAIL 0
- [x] コミット: `feat: add generate_index_md to RBKC` — `22566bc09`

**作業B: terms.json生成をRBKCに新規実装**

現状: `test_terms.py`（29テストGREEN）、`terms.py`、`run.py` 呼び出し追加まで完了済み（未コミット）。
ただし create+verify で **FAIL 発生**（QO3/QO4 が terms.json を通常の knowledge JSON と誤認）。

設計上の問題: index.md と terms.json は知識コンテンツファイルではなくメタデータファイルだが、verify 設計書がこれを未定義のままにしている。ゼロトレランス原則に従い、**設計書更新 → verify TDD → 実装整合** の順で進める。

**作業B-1: verify 設計書の更新**

- [ ] `tools/rbkc/docs/rbkc-verify-quality-design.md` を更新:
  - §0 全体像: 出力ファイルに index.md / terms.json を追加（それぞれの役割を明記）
  - QO4 を index.md ベースに刷新（index.toon 廃止。index.md の網羅性・内容整合性を検証）
  - QO5 新設: terms.json 整合性チェック（存在確認、dangling section 参照検出）
  - QO3/QO4 スキャンから index.md / terms.json を除外する旨を明記
  - §4 品質保証マトリクスに QO5 を追加（❌ 状態）
  - §4 対応テストテーブルに QO4/QO5 のテストクラスを追記

**作業B-2: verify TDD（QO4 更新 + QO5 新設）**

- [ ] `test_verify.py` の `TestCheckIndexCoverage` に index.md 対応テストを追加（RED）
  - index.md 存在チェック、全 content JSON が H3 エントリとして存在、dangling path 検出
- [ ] `test_verify.py` に `TestCheckTermsCoverage` を新規追加（RED）
  - terms.json 存在チェック、section 参照形式（`path:sN`）、dangling 参照検出
- [ ] `verify.py` を更新（GREEN）:
  - `check_index_coverage()`: index.toon → index.md ベースに変更、QO3/QO4 スキャンから terms.json / index.md を除外
  - `check_terms_coverage()` を新規実装
- [ ] 全5バージョンで create+verify: 全バージョン FAIL 0
- [ ] コミット2本:
  - `test: add verify tests for index.md and terms.json coverage`
  - `feat: update verify — QO4 to index.md, add QO5 terms.json`

**作業B-3: 作業Bのコミット**

- [ ] test_terms.py, terms.py, run.py の変更をコミット: `feat: add generate_terms to RBKC`

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

- [x] B-1. 現行検索E2Eベースライン取得 — 3 runs, 精度83.7%, 幻覚PASS14.4%, $59.34 — committed `7ea223ab3`
- [x] qa-current.json を results/baseline-current/ に移動 — `f3d8eeb15`
- [x] HOW-TO-RUN.md を新スキル向けに更新（qa-current.json参照除去） — `b6f7d092f`
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
