# Tasks: 検索改善

**Branch**: search
**Updated**: 2026-05-15

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

### A-1. RBKC変更のリバート

searchブランチに混入したRBKC変更を除去する。RBKCはフェーズBスコープ。

- [ ] `git revert 46893d39f` — P1-group subtype（xlsx_common.py, xlsx-sheet-mapping.md, test_xlsx_common.py）
- [ ] `tools/rbkc/scripts/create/terms.py` を削除（`03e20a535`で追加）
- [ ] `tools/rbkc/tests/ut/test_terms.py` を削除
- [ ] `tools/rbkc/scripts/run.py` のterms関連変更をリバート
- [ ] 既存RBKCテスト全件パス確認（`pytest tools/rbkc/tests/`）

### A-2. 現行スキル変更のリバート

searchブランチから現行スキルへの変更を除去する。

- [ ] `.claude/skills/nabledge-6/scripts/keyword-search.sh` を削除
- [ ] `.claude/skills/nabledge-6/scripts/read-sections.sh` を `git checkout main -- .claude/skills/nabledge-6/scripts/read-sections.sh` でリバート
- [ ] keyword-search.shのテスト（`tools/tests/test-keyword-search.sh` 等）を `tools/benchmark/tests/` に移動（あれば）

### A-3. 部品ディレクトリ整理

部品ファイルを `tools/benchmark/components/` に集約する。

- [ ] `tools/benchmark/components/prompts/` を作成
- [ ] 部品プロンプト6件を `tools/benchmark/prompts/` から `components/prompts/` に移動: hearing-classify.md, hearing-extract.md, semantic-search-stage1.md, semantic-search-stage2.md, answer.md, verify.md
- [ ] `tools/benchmark/prompts/` にはベンチマーク専用（c-claim-judge.md, hallucination-judge.md）のみ残す
- [ ] `tools/benchmark/components/scripts/` を作成
- [ ] `keyword-search.sh` を `components/scripts/` に配置（A-2で削除したスキル版をベースに）
- [ ] `read-sections.sh`（変更版: タイトル出力付き）を `components/scripts/` に配置
- [ ] `answer-generation.md` の扱いを確認（部品 or ベンチマーク専用）→ 適切なディレクトリに配置

### A-4. パス参照の更新

A-3のファイル移動に伴い、参照元を全て更新する。

- [ ] `simulate_hearing.py` — プロンプトパスを `components/prompts/` に変更
- [ ] `simulate_semantic_search.py` — プロンプトパスを `components/prompts/` に変更
- [ ] `simulate_answer.py` — プロンプトパスを `components/prompts/` に変更
- [ ] `simulate_verify.py` — プロンプトパスを `components/prompts/` に変更
- [ ] `simulate_answer_verify.py` — プロンプトパスを `components/prompts/` に変更
- [ ] `run.py` — プロンプトパス + read-sections.sh/keyword-search.shパスを `components/` に変更
- [ ] テスト全件パス確認（`pytest tools/benchmark/tests/`）

### A-5. 設計書の整合

- [ ] `benchmark-design.md` のディレクトリ構成セクションを `search-design.md` の `components/` 構造に合わせて更新
- [ ] 各コンポーネント設計書のファイルパス参照を確認・更新（semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md）

### A-6. マージ

- [ ] searchブランチの成果物をフェーズBブランチにマージ

## マージ後（フェーズB）

依存関係: B-1 → B-2 → B-3 → B-4 → B-5 → B-6。順序を守ること。

### B-1. 現行検索E2Eベースライン取得

**RBKC変更・スキルデプロイの前に実施すること。** 現行検索を変更した後ではベースラインが取れなくなる。

- [ ] E2Eベンチマークランナー（`run_e2e.py`）を実装
- [ ] 現行検索（現行qa.md）でE2Eベンチマーク実行（v6、全QAシナリオ）
- [ ] 結果を `results/baseline-current/` に保存・コミット
- [ ] ベースラインレポートをユーザーに報告

### B-2. RBKC変更

B-1のベースライン取得完了後に実施。

- [ ] セキュリティチェックExcel P1-group subtype — ユーザーレビュー（コードは `46893d39f` を再適用）
- [ ] セキュリティチェックExcel P1-group subtype — コード再適用
- [ ] index.md生成（index.py: index.toon → index.md変更）
- [ ] terms.json出力（terms.py再適用）
- [ ] 全5バージョンで `rbkc.sh create` + `rbkc.sh verify` 実行
- [ ] FAIL数の差分確認、リグレッションなし確認

### B-3. スキルデプロイ

B-2のRBKC変更完了後に実施。

- [ ] `components/prompts/` → `.claude/skills/nabledge-6/assets/` にプロンプトをデプロイ
- [ ] `components/scripts/` → `.claude/skills/nabledge-6/scripts/` にスクリプトをデプロイ
- [ ] `qa.md` ワークフロー作成（オーケストレーション）
- [ ] `semantic-search.md` ワークフロー作成
- [ ] `keyword-search.md` ワークフロー作成
- [ ] `qa/hearing.md` ワークフロー作成
- [ ] `qa/answer.md` ワークフロー作成
- [ ] `qa/verify.md` ワークフロー作成
- [ ] `code-analysis.md` ワークフロー作成
- [ ] 各ワークフローが正常動作することを手動確認

### B-4. 新検索E2Eベンチマーク

B-3のスキルデプロイ完了後に実施。

- [ ] 新検索（新qa.md）でE2Eベンチマーク実行（v6、全QAシナリオ）
- [ ] 結果を `results/v1-new-search/` に保存・コミット
- [ ] 比較レポート生成（baseline-current vs v1-new-search）
- [ ] ユーザーに報告

### B-5. 改善サイクル

B-4の比較で現行未満の項目がある場合に実施。

- [ ] 劣化箇所の原因を部品ベンチマークで特定（部品→E2Eの順で改善）
- [ ] 部品プロンプト・スクリプトを修正
- [ ] 部品ベンチマーク再実行で改善確認
- [ ] E2Eベンチマーク再実行（`results/v{N}-new-search/`）
- [ ] 現行以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後、v6で確定した検索をv5/v1.4/v1.3/v1.2に展開。

- [ ] v5に展開
- [ ] v1.4に展開
- [ ] v1.3に展開
- [ ] v1.2に展開

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
