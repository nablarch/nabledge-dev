# Goal

RAGネイティブのNabledge実装を構築し、現行エージェンティック検索との比較ベンチマークを実施して、RAG採用の可否を証拠に基づいて判定する。

設計書（`docs/reports/rag/rag-nabledge-design.md`）に基づいてRAGパイプライン（Qdrant + Cohere Embed + LlamaIndex）を実装し、現行ベンチマーク（34シナリオ × 3 run）と同条件でE2E評価を行う。計測結果からadopt/rejectの結論を出す。

当初設計の `cohere.embed-v4:0` は SCP でブロックされているため、まず `cohere.embed-multilingual-v3`（512トークン制約あり）で実装・計測を進める。v4のSCP解除後にモデルを差し替えて全件再計測する。

# Acceptance criteria

- RAGパイプライン（Qdrant + Cohere Embed + LlamaIndex）が実装されており、モデルIDを設定で切り替えられる
- RAG版 `run_rag_qa.py` が実装されており、現行と同じ `workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json` を出力する
- v3モデルで v6の全34シナリオが動作し、3 run分のベンチマーク結果が得られている（v3制約の影響は結果に明記）
- 評価レポートが作成されており、現行ベースライン（`20260616-1214-fullbench-classes-v6`）との比較が含まれる
- v4解除後に再Indexing・再計測して v4条件での評価レポートが得られている
- 最終レポートに明確なadopt/reject結論が記載されている

# Assumptions

- Bedrockへの接続は利用可能（Nablarch開発PJ前提）
- DockerとDocker Composeがローカルで利用可能
- 現行JSON知識ファイル（`.claude/skills/nabledge-6/knowledge/`）がIndexingの入力として使用可能
- 現行ベンチマーク（`tools/benchmark/`）のDeepEval評価層・`evaluate.py`・手順骨格はそのまま流用する
- 当面使用するモデル: `cohere.embed-multilingual-v3`（512トークン制約あり、v4解除待ち）
- v4解除後に差し替え予定: `cohere.embed-v4:0`、リージョン: `ap-northeast-1`
- v3の512トークン制約により、シナリオ参照ページの48%（31中15ページ）で入力が切れる — 計測結果はv3の限界を反映する
- 設計書§2.2の事実（JSON構造、規模、メタ導出規則）は正確である

# Rules

- commit and push every change; one completion marker per task
- 設計書（`docs/reports/rag/rag-nabledge-design.md`）の判断を尊重する（変更は設計書更新と一緒に）
- RAGコードは `tools/rag/` ディレクトリに配置する
- 現行ベンチマーク（`tools/benchmark/`）のコードを直接変更しない
- 計測ラベルは `YYYYMMDD-HHMM-rag-k{k}-{filter}` 形式とする（例: `20260625-1000-rag-k10-filter`）
- verify は quality gate — never weaken to make RAG output pass

# Tasks

### #1: Docker環境構築とIndexingスクリプト実装（小規模動作確認まで）

**Purpose**: Qdrant起動のDocker環境を作り、Indexingスクリプトを実装して少数ファイル（10件）で動作を確認する

**Prerequisites**: none

**Steps**:

- [ ] `tools/rag/` ディレクトリ構造を作成する（`docker/`, `scripts/`, `tests/` サブディレクトリ）
- [ ] `tools/rag/docker/docker-compose.yml` を実装する（Qdrant起動、ストレージマウント）
- [ ] `tools/rag/scripts/index.py` を実装する（JSON→chunk→メタ付与→Cohere Embed→Qdrant）
  - section単位チャンク化（`title` + `content` を結合してembed、page `title` を前置）
  - メタデータ付与：`processing_type` / `category` / `page_id` / `section_id` / `title` / `level` / `class_names` / `linked_pages`（パスから機械導出）
  - `input_type=search_document` でCohere Embed v4 Bedrock呼び出し
- [ ] `tools/rag/tests/test_index.py` を実装する（チャンク化・メタ導出のユニットテスト）
- [ ] `docker compose up` でQdrant起動確認
- [ ] **10ファイル限定**でIndexing実行（`--limit 10` オプション等）し、pointが格納されmetadataが正しいことを確認する
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-1.md`）
- [ ] QA expert review（subagent）
- [ ] language expert review（subagent）
- [ ] software-engineering expert review（subagent）
- [ ] user review

**Completion criteria**:

- `tools/rag/docker/docker-compose.yml` が存在し、`docker compose up` でQdrantが起動する
- `tools/rag/scripts/index.py` が `--limit 10 --model cohere.embed-multilingual-v3` で実行でき、Qdrantに10ファイル分のpointが格納される
- 格納されたpointのmetadataに `processing_type` / `category` / `page_id` / `section_id` が含まれている
- 格納された1件の `page_id` を使って、knowledge ディレクトリの対応JSONファイルが実際に開けること（`open(knowledge_dir / page_id + ".json")` が成功する）
- `tools/rag/tests/test_index.py` のテストがすべてパスする
- モデルIDがコマンドライン引数（`--model`）で切り替えられる（v4差し替えに備えて）

### #2: v6全件Indexing実行

**Purpose**: 動作確認済みのIndexingスクリプトでv6の全935ページをQdrantにベクトル化・格納する

**Prerequisites**: #1

**Steps**:

- [ ] Qdrantストレージをリセットして全件Indexingを実行する
- [ ] 完了後にpoint数を確認する（`python3 -c "from qdrant_client import QdrantClient; c=QdrantClient('localhost',port=6333); print(c.get_collection('nabledge_v6').points_count)"`）
- [ ] 1件抽出してmetadataの内容を目視確認する
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-2.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- Qdrantコレクションに9,000件以上のpointが格納されている（設計書§2.2の9,376 sections相当）
- 抽出した1件のmetadataに `processing_type` / `category` / `page_id` / `section_id` / `class_names` が含まれている
- 抽出した1件の `page_id` を使って、knowledge ディレクトリの対応JSONファイルが実際に開けること（`open(knowledge_dir / page_id + ".json")` が成功する）

### #3: RAG版クエリエンジン実装（1シナリオ動作確認まで）

**Purpose**: 質問をベクトル化しQdrant top-k検索するクエリエンジンと、1シナリオを動かす `run_rag_qa.py` を実装する

**Prerequisites**: #2

**Steps**:

- [x] `tools/rag/scripts/query.py` を実装する
  - `input_type=search_query` でCohere Embed v4 Bedrock呼び出し
  - Qdrant top-k検索（k=10 / k=20）
  - メタフィルタ（`processing_type` / `purpose`）
  - 結果を `selected_pages` / `read_sections`（`path.json:sN` 形式）で返す（現行 `workflow_details.json` フォーマット互換）
- [x] `tools/rag/tests/test_query.py` を実装する（クエリ・フィルタのユニットテスト）
- [x] `tools/rag/scripts/run_rag_qa.py` を実装する
  - `query.py` でtop-k取得 → LLMへ渡し回答生成（現行 `e2e-prompt.md` 流用）
  - 現行 `run_qa.py` と同じ出力構造（`workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json`）
- [x] **1シナリオ（`pre-01`）**で実行し、出力を目視確認する
- [x] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-3.md`）
- [x] QA expert review（subagent）
- [x] language expert review（subagent）
- [x] software-engineering expert review（subagent）
- [x] user review

**Completion criteria**:

- `run_rag_qa.py --scenario-ids pre-01` が終了コード0で完了する
- 出力ディレクトリに `workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json` が揃う
- `workflow_details.json` の `step3.selected_sections` が1件以上あること
- `workflow_details.json` の `read_sections` が `path.json:sN` 形式で記録されており、各パスが knowledge ディレクトリに実際に存在すること
- `answer.md` に `(content unavailable)` が含まれないこと（知識セクションが実際に取得・使用されている）
- `tools/rag/tests/test_query.py` のテストがすべてパスする

### #4: 段階的スケールアップ（pre-* 全件 → pre-* + qa-* 前半）

**Purpose**: フルベンチ前に段階的にシナリオ数を増やし、問題があれば早期に修正する

**Prerequisites**: #3

**Steps**:

- [x] `pre-*` 全件（pre-01〜pre-03、3件）で実行し、全件完了・出力正常を確認する
- [x] `qa-*` の前半（qa-01〜qa-10、10件）を追加実行し、完了・出力正常を確認する
- [x] エラー・タイムアウトがあれば原因を調査・修正する
- [x] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-4.md`）
- [x] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `pre-01〜pre-03` + `qa-01〜qa-10` の計13シナリオすべてに `error.json` が存在しないこと
- 各シナリオの `workflow_details.json` の `step3.selected_sections` が1件以上あること
- 各シナリオの `answer.md` に `(content unavailable)` が含まれないこと

### #5: v4差し替え・全件Indexing

**Purpose**: `cohere.embed-v4:0` のSCP解除後、モデルを差し替えてQdrantを全件再Indexingする

**Prerequisites**: #4 + v4 SCP解除

**Steps**:

- [ ] `--model cohere.embed-v4:0` で全件Indexing実行（Qdrantストレージをリセット）
- [ ] point数・metadata確認（#2と同じ受入基準）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-5.md`）
- [ ] user review

**Completion criteria**:

- Qdrantコレクションに9,000件以上のpointが格納されている
- Indexing実行ログに `--model cohere.embed-v4:0` が使用されたことが確認できること（コマンド履歴またはログ出力）
- 抽出した1件の `page_id` を使って、knowledge ディレクトリの対応JSONファイルが実際に開けること

### #6: 全34シナリオ × 3 run ベンチマーク実行

**Purpose**: k=10・メタフィルタありの条件で全34シナリオを3 run実施し、crossrun-summary.md と quality-report.md を生成する

**Prerequisites**: #5

**Steps**:

- [ ] run-1: 全34シナリオ実行 → `HOW-TO-RUN.md` B-2（エラー回収）→ B-3（レポート生成）→ B-4（コミット）
- [ ] run-2: 同上
- [ ] run-3: 同上
- [ ] フェーズC-1: crossrun-summary.md 生成・コミット
- [ ] フェーズC-2: 閾値割れシナリオの裏付け調査（answer.md とナレッジの突き合わせ）
- [ ] フェーズC-3: quality-report.md 作成・コミット（現行ベースライン `20260616-1214-fullbench-classes-v6` との比較を含む）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-6.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- run-1 / run-2 / run-3 の全34シナリオ × 3 runに `error.json` が存在しないこと
- `crossrun-summary.md` に全34シナリオのスコアが記載されている
- `quality-report.md` に pass rate（数値）が含まれている
- `quality-report.md` に現行ベースライン（`20260616-1214-fullbench-classes-v6`）との比較が含まれている

### #7: 採用判定レポート作成

**Purpose**: 計測結果を総括し、必要に応じて追加計測を行い、RAG採用の可否を結論づける評価レポートを作成する

**Prerequisites**: #6

**Steps**:

- [ ] #6の結果を評価する（34シナリオ全パスかどうか）
- [ ] 必要に応じてk=20 / naive（フィルタなし）条件を追加計測する（設計書§7.2）
- [ ] 必要に応じてCohere Rerank 3.5を投入して再計測する（設計書§7.3 step 6）
- [ ] `docs/reports/rag/rag-evaluation-report.md` を作成する
  - 計測条件・結果サマリー
  - 現行エージェンティック検索との比較（精度・コスト・速度）
  - 語彙ギャップ分析（miss/partialシナリオの原因分析）
  - 明確なadopt/reject結論と理由
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-7.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `docs/reports/rag/rag-evaluation-report.md` が存在する
- レポートに現行比較の具体的な数値（pass rate・コスト・速度）が含まれている
- レポートのadopt/reject結論に、その根拠として使った数値が明示されている
- Issue #383のSuccess Criteriaが満たされている（v6ベンチ結果取得・評価レポート作成・adopt/reject結論）


# Decisions

## D-1: v3で先行実装・v4解除後に差し替え
- **Issue**: `cohere.embed-v4:0` が SCP でブロック。v3（512トークン制約）で進めるか、v4解除を待つか
- **Conclusion**: v3で実装・動作確認（#1〜#4）を進め、フルベンチ（#6）はv4解除後に実施する
- **Rationale**: v3でパイプライン全体の動作確認はできる。フルベンチはv4解除後に一度だけ実施すれば十分で、v3での中間計測は不要
- **Evidence**: シナリオ参照ページ31中15ページ（48%）がv3の512トークン制約を超える。v4は128Kトークン・最安値（$0.02/1M）・東京対応
- **Sources**: 実測（binary search）、AWS公式ドキュメント

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
