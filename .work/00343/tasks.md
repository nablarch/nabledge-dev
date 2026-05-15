# Tasks: 検索改善

**Branch**: search
**Updated**: 2026-05-15

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
- [ ] searchブランチの成果物をフェーズBブランチにマージ

## マージ後（フェーズB）

依存関係: B-1 → B-2 → B-3 → B-4 → B-5 → B-6。順序厳守。

### B-1. 現行検索E2Eベースライン取得

**RBKC変更・スキルデプロイの前に実施すること。** 変更後はベースラインが取れなくなる。

- [ ] E2Eベンチマーク設計を確定（benchmark-design.md のE2Eセクション）
- [ ] E2Eベンチマークランナー（`run_e2e.py`）のテストを書く（RED）
- [ ] `run_e2e.py` を実装（GREEN）
- [ ] 現行検索（現行qa.md）で1シナリオ実行して動作確認
- [ ] 全QAシナリオでE2Eベンチマーク実行（v6）
- [ ] 結果を `results/baseline-current/` に保存・コミット
- [ ] ベースラインレポートをユーザーに報告

### B-2. RBKC変更

B-1完了後に実施。

- [ ] `git cherry-pick 46893d39f` — P1-group subtype再適用（xlsx_common.py, xlsx-sheet-mapping.md, test_xlsx_common.py）
- [ ] テスト確認: `pytest tools/rbkc/tests/ut/test_xlsx_common.py -x`
- [ ] P1-group subtype — ユーザーレビュー
- [ ] `git cherry-pick 03e20a535` — terms.py + test_terms.py + run.py terms統合を再適用
- [ ] テスト確認: `pytest tools/rbkc/tests/ut/test_terms.py -x`
- [ ] index.md生成（index.py: index.toon → index.md変更）のテストを書く（RED）
- [ ] index.py を実装（GREEN）
- [ ] 全5バージョンで `rbkc.sh create` + `rbkc.sh verify` 実行
- [ ] FAIL数の差分確認、リグレッションなし確認

### B-3. スキルデプロイ

B-2完了後に実施。

- [ ] `components/prompts/` → `.claude/skills/nabledge-6/assets/` にデプロイ
- [ ] `components/scripts/` → `.claude/skills/nabledge-6/scripts/` にデプロイ
- [ ] `qa/hearing.md` ワークフロー作成
- [ ] `semantic-search.md` ワークフロー作成
- [ ] `keyword-search.md` ワークフロー作成
- [ ] `qa/answer.md` ワークフロー作成
- [ ] `qa/verify.md` ワークフロー作成
- [ ] `qa.md` ワークフロー作成（オーケストレーション）
- [ ] `code-analysis.md` ワークフロー作成
- [ ] 1シナリオで手動動作確認

### B-4. 新検索E2Eベンチマーク

B-3完了後に実施。

- [ ] 新検索（新qa.md）で1シナリオ実行して動作確認
- [ ] 全QAシナリオでE2Eベンチマーク実行（v6）
- [ ] 結果を `results/v1-new-search/` に保存・コミット
- [ ] 比較レポート生成（baseline-current vs v1-new-search）
- [ ] ユーザーに報告

### B-5. 改善サイクル

B-4の比較で現行未満の項目がある場合に実施。改善は部品→E2Eの順。

- [ ] 劣化箇所の原因を部品ベンチマークで特定
- [ ] 部品プロンプト・スクリプトを修正
- [ ] 部品ベンチマーク再実行で改善確認
- [ ] E2Eベンチマーク再実行（`results/v{N}-new-search/`）
- [ ] 現行以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後、v6で確定した検索を展開。

- [ ] v5に展開
- [ ] v1.4に展開
- [ ] v1.3に展開
- [ ] v1.2に展開

### B-7. nabledge-test削除

B-6完了後に実施。新ベンチマーク基盤で置き換え済みのため不要。

- [ ] `tools/tests/test-setup.sh`: `_scenario_field`関数を削除、質問・キーワードをハードコード（各バージョン1問ずつ）
- [ ] `.claude/skills/nabledge-test/` ディレクトリ削除
- [ ] `.claude/agents/nabledge-test-runner.md` 削除
- [ ] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除
- [ ] `.claude/rules/` 内のnabledge-test固有の記述を削除（`temporary-files.md`, `nabledge-skill.md`）
- [ ] 動作確認: `bash tools/tests/test-setup.sh` を実行し全バージョンのverify成功を確認
- [ ] 動作確認: `python3 -m pytest tools/ -x` で全テストパス

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
