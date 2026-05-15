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

searchブランチに混入したRBKC変更を除去する。ベンチマークからの参照なし — 影響はRBKCテストのみ。

**影響範囲:**
- `tools/rbkc/scripts/create/converters/xlsx_common.py` — P1-group追加分
- `tools/rbkc/docs/xlsx-sheet-mapping.md` — P1-group記述
- `tools/rbkc/tests/ut/test_xlsx_common.py` — P1-groupテスト
- `tools/rbkc/scripts/create/terms.py` — 新規ファイル
- `tools/rbkc/tests/ut/test_terms.py` — 新規ファイル
- `tools/rbkc/scripts/run.py` — terms関連の変更

**Steps:**
- [ ] `git revert --no-commit 46893d39f`（P1-group subtype）
- [ ] 既存RBKCテストパス確認: `pytest tools/rbkc/tests/ -x`
- [ ] コミット・プッシュ
- [ ] `tools/rbkc/scripts/create/terms.py` と `tools/rbkc/tests/ut/test_terms.py` を削除
- [ ] `tools/rbkc/scripts/run.py` のterms関連変更をリバート
- [ ] 既存RBKCテストパス確認: `pytest tools/rbkc/tests/ -x`
- [ ] コミット・プッシュ

### A-2. 設計書の整合（ディレクトリ構成）

実装前に設計書を確定する。`search-design.md` の `components/` 構造に他の設計書を合わせる。

**影響範囲:**
- `benchmark-design.md` 503-541行 — ディレクトリ構成セクションが旧構造のまま
- 各コンポーネント設計書 — ファイルパス参照があれば更新

**Steps:**
- [ ] `benchmark-design.md` のディレクトリ構成を `components/` 構造に更新
- [ ] `answer-generation.md` の位置づけを確認（部品 → `components/prompts/` or ベンチマーク専用 → `prompts/`）
- [ ] コンポーネント設計書4本のファイルパス参照を確認・必要なら更新
- [ ] コミット・プッシュ

### A-3. 部品プロンプトの移動

設計書に合わせ、部品プロンプトを `components/prompts/` に移動する。
ベンチマーク専用（judge）は `prompts/` に残す。

**影響範囲（PROMPTS_DIR参照ファイル）:**
- `simulate_hearing.py` → `hearing-classify.md`, `hearing-extract.md`
- `simulate_semantic_search.py` → `semantic-search-stage1.md`, `semantic-search-stage2.md`
- `simulate_answer_verify.py` → `answer.md`, `verify.md`
- `run.py` → `answer-generation.md`（A-2で位置づけ確定後）
- `evaluate.py` → `c-claim-judge.md`, `hallucination-judge.md`（変更不要 — `prompts/` に残る）

**Steps（段階的に — 1件で動作確認後に残り）:**
- [ ] `tools/benchmark/components/prompts/` ディレクトリ作成
- [ ] `hearing-classify.md`, `hearing-extract.md` を `components/prompts/` に移動
- [ ] `simulate_hearing.py` のプロンプトパスを `components/prompts/` に変更
- [ ] テスト確認: `pytest tools/benchmark/tests/test_simulate_hearing.py -x`
- [ ] コミット・プッシュ
- [ ] 残り4件を移動: `semantic-search-stage1.md`, `semantic-search-stage2.md`, `answer.md`, `verify.md`
- [ ] `simulate_semantic_search.py`, `simulate_answer_verify.py` のプロンプトパスを変更
- [ ] テスト確認: `pytest tools/benchmark/tests/ -x`
- [ ] `answer-generation.md` をA-2の決定に従い配置、`run.py` のパスを更新
- [ ] テスト確認: `pytest tools/benchmark/tests/test_run.py -x`
- [ ] 全テスト確認: `pytest tools/benchmark/tests/ -x`
- [ ] コミット・プッシュ

### A-4. 部品スクリプトの移動

`keyword-search.sh` と `read-sections.sh`（変更版）を `components/scripts/` に配置し、現行スキルへの変更をリバートする。

**影響範囲:**
- `.claude/skills/nabledge-6/scripts/keyword-search.sh` — 新規追加（mainに存在しない）
- `.claude/skills/nabledge-6/scripts/read-sections.sh` — タイトル出力追加（mainと差分あり）
- `tools/tests/test_keyword_search.py` — スキルディレクトリの `keyword-search.sh` を直接参照（20テスト）

**ベンチマークPythonスクリプトへの影響: なし。** `simulate_*.py` と `run.py` は `keyword-search.sh` も `read-sections.sh` も参照していない（セクション読み込みは `evaluate.py` の `load_section_content()` でJSON直接読み）。

**Steps（段階的に）:**
- [ ] `tools/benchmark/components/scripts/` ディレクトリ作成
- [ ] `keyword-search.sh` を `.claude/skills/nabledge-6/scripts/` から `components/scripts/` にコピー
- [ ] `read-sections.sh`（変更版）を `.claude/skills/nabledge-6/scripts/` から `components/scripts/` にコピー
- [ ] `tools/tests/test_keyword_search.py` の `SCRIPT_PATH` を `components/scripts/keyword-search.sh` に変更
- [ ] テスト確認: `pytest tools/tests/test_keyword_search.py -x`
- [ ] コミット・プッシュ
- [ ] `.claude/skills/nabledge-6/scripts/keyword-search.sh` を削除
- [ ] `git checkout main -- .claude/skills/nabledge-6/scripts/read-sections.sh` でリバート
- [ ] コミット・プッシュ
- [ ] 全テスト確認: `pytest tools/benchmark/tests/ tools/tests/test_keyword_search.py -x`

### A-5. マージ

- [ ] 全テスト最終確認
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

- [ ] セキュリティチェックExcel P1-group subtype — A-1でリバートしたコードを再適用
- [ ] P1-group subtype — ユーザーレビュー
- [ ] terms.py — A-1で削除したコードを再適用
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
