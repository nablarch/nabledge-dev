# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-19

## In Progress

### B-4-0. run_e2e.py 調査・修正

B-4実行中に判明した問題を先に修正する。

**課題**:

1. **連続実行時のクラッシュ（原因未特定）**
   - 単体実行は正常（pre-01〜review-09, impact-01, impact-03 すべて単体OK）
   - 連続実行すると `ValueError: Marker not found in response: <<<BENCHMARK_HEARING>>>` でクラッシュ
   - run-1（20260519-083929）: review-08でタイムアウト（360s）→ クラッシュ
   - run-2（20260519-091236）: review-08/09完了後、impact-01でクラッシュ（同じエラー）
   - 失敗シナリオがログに出ないため現状は特定不能

2. **エラーハンドリング不在**
   - 1件失敗すると後続シナリオがすべてスキップされる
   - どのシナリオで何が起きたかstderrに出ない
   - summary.jsonが生成されないため何件成功したかも分からない
   - SEレビューで見落とされた（既存テストにエラー系ケースがない）

**調査ステップ**:
- [ ] 調査1: `run_e2e.py` のclaude CLI呼び出し部分を読み、タイムアウト・レスポンス欠損が起きる条件を特定
  - `TIMEOUT = 360` の根拠を確認（HOW-TO-RUN.md / 設計書に記載があるか）
  - タイムアウト時にclaudeが返すレスポンスの形式を確認（マーカーなしのテキストが返るか、例外か）
  - `<<<BENCHMARK_HEARING>>>` マーカーが欠損するケースを設計書・ワークフローで確認
- [ ] 調査2: 既存テストのカバレッジ確認
  - `tools/benchmark/tests/` でrun_e2e関連テストを列挙
  - エラー系（タイムアウト・マーカー欠損・不正JSON）のテストケースがあるか確認
- [ ] 調査結果をユーザーに報告してから修正方針を確定

**修正ステップ（調査後に詳細化）**:
- [ ] RED: 根本原因に対するテストを追加
- [ ] テストがREDであることを確認（`pytest tools/benchmark/tests/ -x -k run_e2e`）
- [ ] GREEN: 根本原因を修正（エラーハンドリング改善はあわせて実施）
- [ ] テストがGREENであることを確認（`pytest tools/benchmark/tests/ -x`）
- [ ] SEレビュー（別エージェント）
- [ ] コミット・プッシュ
- [ ] 落ちたシナリオのみ `--scenario-ids` で再実行して問題解消を確認
  - 受入条件: 終了コード0、対象シナリオが全件完了すること

### B-4. 新スキルE2Eベンチマーク

B-4-0完了後に実施。

- [ ] run-1 実行（全30シナリオ）:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .claude/skills/nabledge-6
  ```
  - 受入条件: 終了コード0、`total_scenarios` = 30、`summary.json` の `scenarios_file` が `qa.json` であること
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

### B-8. test-setup.sh 動作確認

B-7完了後、mainマージ → nablarch/nabledge:develop自動sync後に実施。
**前提**: mainマージ済みであること（test-setup.sh は nablarch/nabledge:develop からスキルを取得するため）

**確認対象**:
- `test-setup.sh` は GUIDE-CC.md / GUIDE-GHC.md からsetupスクリプトURLを取得
- setupスクリプトでスキルをインストール（静的チェック: SKILL.md / knowledge/ / docs/ / コマンドファイル）
- 動的チェック: `claude -p` でSKILL.mdが読まれるか（B-7で `_scenario_field` を削除してハードコードに変更済み）
- 全バージョン（v6/v5/v1.4/v1.3/v1.2/upgrade）× CC/GHC

**ステップ**:
- [ ] v6のみ先行確認:
  ```bash
  cd .tmp/nabledge-test-b8 && bash /path/to/tools/tests/test-setup.sh v6
  ```
  - 受入条件: 終了コード0、静的チェックOK、動的チェックOK（SKILL.md read）
- [ ] 問題があればB-7の修正内容を確認・修正してコミット
- [ ] 全バージョン確認:
  ```bash
  bash tools/tests/test-setup.sh
  ```
  - 受入条件: 終了コード0、全環境 `[OK]` のみ

## Done

- [x] B-2. RBKC変更（index.md + terms.json生成）— `22566bc09`, `c05a3afac`, `84f2feb23`, `cc5d2c56b`, `38fe7aae9`, `b3f0c9dfe`
- [x] B-1. 現行検索E2Eベースライン取得 — 3 runs, 精度83.7%, 幻覚PASS14.4%, $59.34 — committed `7ea223ab3`
- [x] qa-current.json を results/baseline-current/ に移動 — `f3d8eeb15`
- [x] HOW-TO-RUN.md を新スキル向けに更新（qa-current.json参照除去） — `b6f7d092f`
- [x] B-3. スキルデプロイ（スモークテスト完了） — `a07583fc4`, `549df22d2`, `000fc91db`, `71a0c16e3`, `10a7aaf82`
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
