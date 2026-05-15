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

### ディレクトリ整理

設計書に合わせ、部品ファイルを `tools/benchmark/components/` に集約する。現行スキルへの変更をリバートする。

- [ ] `tools/benchmark/components/prompts/` を作成、部品プロンプト6件を `prompts/` から移動（hearing-classify, hearing-extract, semantic-search-stage1, semantic-search-stage2, answer, verify）
- [ ] `tools/benchmark/components/scripts/` を作成、`keyword-search.sh` と `read-sections.sh`（変更版）を配置
- [ ] `.claude/skills/nabledge-6/scripts/keyword-search.sh` を削除
- [ ] `.claude/skills/nabledge-6/scripts/read-sections.sh` をmainの状態にリバート
- [ ] シミュレーションスクリプト（`simulate_*.py`, `run.py`）のパス参照を更新
- [ ] `benchmark-design.md` のディレクトリ構成を `search-design.md` に合わせて更新
- [ ] テスト全件パス確認

### セキュリティチェックExcel — ユーザーレビュー

P1-group subtype実装済み（`46893d39f`）。create+verify実行はフェーズB。

- [ ] ユーザーレビュー

### マージ

- [ ] search ブランチの成果物をフェーズBブランチにマージ

## マージ後（フェーズB）

### RBKC変更

- [ ] index.md生成（index.py: index.toon → index.md）
- [ ] terms.json出力（terms.py）
- [ ] セキュリティチェックExcel — 全5バージョンで create+verify 実行

### スキルデプロイ

- [ ] `components/` から `.claude/skills/nabledge-6/` へ部品をデプロイ（prompts → assets/, scripts → scripts/）
- [ ] ワークフロー作成（qa.md, semantic-search.md, keyword-search.md, qa/hearing.md, qa/answer.md, qa/verify.md）
- [ ] code-analysis.md 作成

### E2Eベンチマーク

- [ ] 現行検索ベースライン取得（v6）
- [ ] 新検索E2E実行（v6）
- [ ] 現行 vs 新 比較 → 現行以上になるまで改善（部品→E2Eの順）

### バージョン展開

- [ ] v5/v1.4/v1.3/v1.2 に展開

## Done

### ベンチマーク基盤

評価エンジン（`evaluate.py`, 54テストGREEN）とランナー群（`simulate_*.py`, `run.py`, 23テストGREEN）。QAシナリオ15件、キーワード検索シナリオ12件。SE/QAレビュー済。

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

### RBKC: セキュリティチェックExcel構造修正（コード実装）

P1-group subtype: No列をグループキーに脆弱性単位でセクション統合（50→11セクション）。11テストGREEN, 596既存テストパス。create+verify実行はフェーズB。

### 設計書

`design/` に6本整理: search-design.md, benchmark-design.md, semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md。
