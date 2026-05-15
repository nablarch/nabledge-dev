# Tasks: 検索改善

**Branch**: search
**Updated**: 2026-05-15 (B-1 run_e2e.py実装完了)

## Done

- [x] A-1. RBKC変更のリバート — committed `5bf479e1c`, `f0249fea0`
- [x] A-2. 設計書の整合（ディレクトリ構成） — committed `b3819fb94`
- [x] A-3. 部品プロンプトの移動 — committed `eea31f065`, `426b9a0f4`
- [x] A-4. read-sections.sh テスト追加 — committed `b65064dce` (jq bugfix included, all 5 versions)
- [x] A-5. 部品スクリプトの移動 — committed `d2e6db620`, `0724b3faa`
- [x] A-6. マージ準備完了 — 284 tests pass, diff clean (no skill/RBKC changes)

## Rules

- **数字を実際に読め**: ログや diff を目で確認する。サイズや形から推測しない。
- **答えを先に決めるな**: データが結論を導く。先入観・推測・仮説でバイアスをかけて調査してはいけない。観察した事実だけを報告し、原因不明なら「不明」と言う。
- **ベンチマークで調整するな**: シナリオを使って問題を探すのはOK。そのシナリオに合わせてスコアを調整するのはNG。
- **自己評価禁止**: ベンチマーク結果は必ず別エージェント（QA Expert）に評価させる。実装した本人が採点しない。
- **勝手に直すな**: バグや問題を見つけたら、専門家（SE / PE / QA）に相談してから実装する。
- **出来レース禁止**: シミュレーションは全シナリオ対象。特定シナリオ向けのチューニングは禁止。汎用性能のみ追求する。
- **シミュレーションは全件**: シミュレーション（トレース）は全シナリオで改善を繰り返す。コストゼロなので出し惜しみしない。
- **バイアス排除**: シミュレーション、エキスパートレビュー、改善はそれぞれ別コンテキスト（別エージェント）で実施。メインエージェントが最終判断。
- **調査は網羅的に**: 全バージョン（v6/v5/v1.4/v1.3/v1.2）、幅広いタイプの知識ファイルを対象。
- **設計書は常に最新状態**: （変更）（既存）（旧xxx）等の履歴注釈を入れない。gitが履歴を管理している。後から読むとノイズになる。
- **成果物はエキスパートレビュー後に使用**: プロンプト→PE、スクリプト・コード→SE。ベストプラクティスに従っているかを確認してから使用する。レビュー前の成果物は使わない。
- **バイアス排除（改善サイクル）**: シミュレーション結果の分析→QA（生データから独立分析）、改善提案→PE（QAの分析を受けて）。メインエージェントは生データを渡すだけで分析・結論を注入しない。
- **作業指示は迷わず実行できる粒度**: 各タスクのステップはルールに従った具体的な作業指示とする。曖昧なステップは作業開始前に具体化する。
- **やり直し時は旧成果物を削除**: 作業をやり直す場合、旧成果物（プロンプト、レビュー結果、中間ファイル等）を全て削除してプッシュしてから再開する。ノイズを残さない。
- **プロンプトは手順型で書く**: ルールベース（判断基準の羅列）ではなく、作業手順（明確な命令で実行順序を記述）で書く。LLMが何をどの順番でやるか迷わない形にする。
- **シナリオのmustは本文で検証**: mustセクションの妥当性はタイトルではなく本文を読んで判断する。タイトルだけで「必須」と設定しない。

## マージ前（フェーズA残タスク）

フェーズAの原則: 現行スキル・RBKCは一切変更しない。部品はすべて `tools/benchmark/` 内。

### A-6. マージ

- [x] 全テスト最終確認: 284 passed
- [x] searchブランチの成果物をフェーズBブランチにマージ — committed `8d95af52e`

## マージ後（フェーズB）

依存関係: B-1 → B-2 → B-3 → B-4 → B-5 → B-6。順序厳守。

### B-1. 現行検索E2Eベースライン取得

**RBKC変更・スキルデプロイの前に実施すること。** 変更後はベースラインが取れなくなる。

- [x] E2Eベンチマーク設計を確定（benchmark-design.md のE2Eセクション）
- [x] E2Eベンチマークランナー（`run_e2e.py`）のテストを書く（RED）
- [x] `run_e2e.py` を実装（GREEN）— committed `a4d4403f1`
- [ ] `run_e2e.py` の出力データ品質を修正してからベースライン取得（下記2件）
  - [ ] `model_usage` を `modelUsage`（camelCase）から変換するよう修正: `claude_output.get("modelUsage", {})` に変更（テストも更新）
  - [ ] `usage.input_tokens` が全ターン合算値かを確認: `claude -p --output-format json` のJSONフィールド定義を実測で確認し、全ターン合算でなければ合算フィールドに切り替える
  - [ ] 上記修正後 `pytest tools/benchmark/tests/ -x` でグリーン確認
- [ ] 現行検索（現行qa.md）で1シナリオ実行して動作確認（合格基準）
  - `hearing.json` に `status` フィールドがある
  - `search.json` の `section_ids` が1件以上（現行検索は必ず何か返す）
  - `answer.md` が空でない
  - `metrics.json` の `model_usage` が `{}` でない（`claude-sonnet-4-6` キーが入っている）
  - `metrics.json` の `usage.input_tokens` が1000以上（8ターン会話の合算として妥当）
- [ ] 全QAシナリオでE2Eベンチマーク実行（v6）: `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --output-dir tools/benchmark/results/baseline-current`
  - 実行完了後: `results/baseline-current/` に全シナリオ分のディレクトリが存在する
  - エラーで中断したシナリオがないこと（summary.json の `total_scenarios` = 28）
- [ ] 結果を `results/baseline-current/` に保存・コミット
- [ ] ベースラインレポートをユーザーに報告（シナリオ別の search_sections 件数と hearing_status を一覧）

### B-2. RBKC変更

B-1完了後に実施。

- [ ] `git cherry-pick 46893d39f` — P1-group subtype再適用（xlsx_common.py, xlsx-sheet-mapping.md, test_xlsx_common.py）
  - cherry-pick 後に `git diff HEAD~1 --stat` で3ファイルのみ変更されていること
- [ ] `pytest tools/rbkc/tests/ut/test_xlsx_common.py -x` がグリーン
- [ ] P1-group subtype の変更内容をユーザーに提示し承認取得（承認なしで次に進まない）
- [ ] `git cherry-pick 03e20a535` — terms.py + test_terms.py + run.py terms統合を再適用
  - cherry-pick 後に `git diff HEAD~1 --stat` で対象3ファイルのみ変更されていること
- [ ] `pytest tools/rbkc/tests/ut/test_terms.py -x` がグリーン
- [ ] index.md生成（index.py: index.toon → index.md変更）のテストを書く（RED）: `pytest tools/rbkc/tests/ut/test_index.py` が FAIL
- [ ] index.py を実装（GREEN）: `pytest tools/rbkc/tests/ut/test_index.py` が PASS
- [ ] 全5バージョンで `bash rbkc.sh create v6 && bash rbkc.sh verify v6`（v5/v1.4/v1.3/v1.2も同様）
  - 変更前のFAIL数を記録し、変更後と比較。想定外の増加がないこと

### B-3. スキルデプロイ

B-2完了後に実施。

- [ ] `components/prompts/` → `.claude/skills/nabledge-6/assets/` にデプロイ
  - デプロイ後: `diff tools/benchmark/components/prompts/ .claude/skills/nabledge-6/assets/` で差分なし
- [ ] `components/scripts/` → `.claude/skills/nabledge-6/scripts/` にデプロイ
  - デプロイ後: `diff tools/benchmark/components/scripts/ .claude/skills/nabledge-6/scripts/` で差分なし（既存ファイルとの競合に注意）
- [ ] `qa/hearing.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] `semantic-search.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] `keyword-search.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] `qa/answer.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] `qa/verify.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] `qa.md` ワークフロー作成（オーケストレーション）（PEレビュー後にコミット）
- [ ] `code-analysis.md` ワークフロー作成（PEレビュー後にコミット）
- [ ] 1シナリオで手動動作確認（合格基準）
  - qa.md がBASHエラーなく完了する
  - 回答が日本語で出力されている
  - 回答に `参照:` セクションがある

### B-4. 新検索E2Eベンチマーク

B-3完了後に実施。

- [ ] 新検索（新qa.md）で1シナリオ実行して動作確認（B-1と同じ合格基準を適用）
- [ ] 全QAシナリオでE2Eベンチマーク実行（v6）: `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --output-dir tools/benchmark/results/v1-new-search`
  - `summary.json` の `total_scenarios` = 28（エラー中断なし）
- [ ] 結果を `results/v1-new-search/` に保存・コミット
- [ ] 比較レポート生成（baseline-current vs v1-new-search）: report.py の比較機能で出力
- [ ] QAエキスパートに比較レポートを渡して評価させる（実装者が自己採点しない）
- [ ] ユーザーに報告（QAエキスパートの評価結果を添付）

### B-5. 改善サイクル

B-4の比較で現行未満の項目がある場合に実施。改善は部品→E2Eの順。

- [ ] QAエキスパートの評価から劣化シナリオを特定（シナリオIDと劣化軸を列挙）
- [ ] 劣化原因を部品ベンチマークで特定（`simulate_*.py` で当該シナリオを個別実行）
  - 原因が特定できたら PE/SE に改善案を相談してから実装（勝手に直さない）
- [ ] 部品プロンプト・スクリプトを修正（PEレビュー後にコミット）
- [ ] 部品ベンチマーク再実行で改善確認（当該シナリオのスコアが改善していること）
- [ ] E2Eベンチマーク再実行（`results/v{N}-new-search/`）
- [ ] QAエキスパートによる再評価
- [ ] 全シナリオで baseline-current 以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後、v6で確定した検索を展開。各バージョンで以下を繰り返す。

- [ ] v5に展開
  - ワークフロー・アセット・スクリプトをv5スキルにコピー（パス置換のみ）
  - `python3 -m tools.benchmark.scripts.run_e2e --skill-dir .claude/skills/nabledge-5 --output-dir tools/benchmark/results/v5-new-search` で1シナリオ動作確認
- [ ] v1.4に展開（同上）
- [ ] v1.3に展開（同上）
- [ ] v1.2に展開（同上）

### B-7. nabledge-test削除

B-6完了後に実施。新ベンチマーク基盤で置き換え済みのため不要。

- [ ] `tools/tests/test-setup.sh` で `_scenario_field` 関数を削除し、質問・キーワードをハードコード（各バージョン1問ずつ）
  - 変更後: `bash tools/tests/test-setup.sh` が全バージョンでエラーなく完了
- [ ] `.claude/skills/nabledge-test/` ディレクトリ削除
- [ ] `.claude/agents/nabledge-test-runner.md` 削除
- [ ] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除（`grep nabledge-test .claude/settings.json` で0件になること）
- [ ] `.claude/rules/temporary-files.md` と `nabledge-skill.md` からnabledge-test固有記述を削除
- [ ] `python3 -m pytest tools/ -x` で全テストパス（削除後もグリーン）

## Done

### ベンチマーク基盤

評価エンジン（`evaluate.py`, 54テストGREEN）とランナー群（`simulate_*.py`, `run.py`, 23テストGREEN）。QAシナリオ15件（`qa.json`）、キーワード検索シナリオ12件（`keyword-search.json`）。SE/QAレビュー済。

### 意味検索

2段階方式（Stage1: カテゴリ選定 → Stage2: セクション選定）。プロンプト: `semantic-search-stage1.md`, `semantic-search-stage2.md`。部品ベンチマーク: 97.4%（37/38 must）。ユーザー承認済。

### 回答生成

知識セクションから引用付き回答を生成。プロンプト: `answer.md`。部品ベンチマーク: 18/26 Stable PASS, 1 Stable FAIL（既知）, 7 Unstable。PE/SEレビュー済、ユーザー承認済。

### 根拠検証

回答のハルシネーションを検出。プロンプト: `verify.md`。部品ベンチマーク: FP率5%, FN率0%。PEレビュー済、ユーザー承認済。

### ヒアリング

事実ベース分類（明示キーワードリスト照合、推測禁止）。プロンプト: `hearing-classify.md`, `hearing-extract.md`。部品ベンチマーク: 分類100%, 処理方式100% × 3回完全一致。PEレビュー済、ユーザー承認済。

### キーワード検索

terms.jsonによるキーワードマッチ。case-insensitive部分一致、ページAND+セクションOR。スクリプト: `keyword-search.sh`（20テストGREEN）。

### 設計書

`design/` に6本整理: search-design.md, benchmark-design.md, semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md。
