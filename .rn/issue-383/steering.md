# Goal

RAGネイティブのNabledge実装を構築し、現行エージェンティック検索との比較ベンチマークを実施して、RAG採用の可否を証拠に基づいて判定する。

設計書（`docs/reports/rag/rag-nabledge-design.md`）に基づいてRAGパイプライン（Qdrant + Cohere Embed v4 + LlamaIndex）を実装し、現行ベンチマーク（34シナリオ × 3 run）と同条件でE2E評価を行う。計測結果からadopt/rejectの結論を出す。

# Acceptance criteria

- 設計書の技術スタック（Qdrant, Cohere Embed v4, LlamaIndex）に基づいてIndexingパイプラインが実装されている
- RAG版 `run_qa.py` が実装されており、現行と同じ `workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json` を出力する
- v6の全34シナリオで3 run分のE2Eベンチマーク結果が得られている
- 評価レポート（`quality-report.md`）が作成されており、現行ベースライン（`20260616-1214-fullbench-classes-v6`）との比較が含まれる
- レポートに明確なadopt/reject結論が記載されている

# Assumptions

- Bedrockへの接続は利用可能（Nablarch開発PJ前提）
- DockerとDocker Composeがローカルで利用可能
- 現行JSON知識ファイル（`.claude/skills/nabledge-6/knowledge/`）がIndexingの入力として使用可能
- 現行ベンチマーク（`tools/benchmark/`）のDeepEval評価層・`evaluate.py`・手順骨格はそのまま流用する
- Cohere Embed v4 BedrockモデルID: `cohere.embed-v4:0`、リージョン: `ap-northeast-1`
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
- `tools/rag/scripts/index.py` が `--limit 10` で実行でき、Qdrantに10ファイル分のpointが格納される
- 格納されたpointのmetadataに `processing_type` / `category` / `page_id` / `section_id` が含まれている
- `tools/rag/tests/test_index.py` のテストがすべてパスする

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

### #3: RAG版クエリエンジン実装（1シナリオ動作確認まで）

**Purpose**: 質問をベクトル化しQdrant top-k検索するクエリエンジンと、1シナリオを動かす `run_rag_qa.py` を実装する

**Prerequisites**: #2

**Steps**:

- [ ] `tools/rag/scripts/query.py` を実装する
  - `input_type=search_query` でCohere Embed v4 Bedrock呼び出し
  - Qdrant top-k検索（k=10 / k=20）
  - メタフィルタ（`processing_type` / `purpose`）
  - 結果を `selected_pages` / `read_sections`（`path.json:sN` 形式）で返す（現行 `workflow_details.json` フォーマット互換）
- [ ] `tools/rag/tests/test_query.py` を実装する（クエリ・フィルタのユニットテスト）
- [ ] `tools/rag/scripts/run_rag_qa.py` を実装する
  - `query.py` でtop-k取得 → LLMへ渡し回答生成（現行 `e2e-prompt.md` 流用）
  - 現行 `run_qa.py` と同じ出力構造（`workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json`）
- [ ] **1シナリオ（`pre-01`）**で実行し、出力を目視確認する
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-3.md`）
- [ ] QA expert review（subagent）
- [ ] language expert review（subagent）
- [ ] software-engineering expert review（subagent）
- [ ] user review

**Completion criteria**:

- `run_rag_qa.py --scenario-ids pre-01` が終了コード0で完了する
- 出力ディレクトリに `workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json` が揃う
- `workflow_details.json` の `read_sections` が `path.json:sN` 形式で記録されている
- `tools/rag/tests/test_query.py` のテストがすべてパスする

### #4: 段階的スケールアップ（pre-* 全件 → pre-* + qa-* 前半）

**Purpose**: フルベンチ前に段階的にシナリオ数を増やし、問題があれば早期に修正する

**Prerequisites**: #3

**Steps**:

- [ ] `pre-*` 全件（pre-01〜pre-03、3件）で実行し、全件完了・出力正常を確認する
- [ ] `qa-*` の前半（qa-01〜qa-10、10件）を追加実行し、完了・出力正常を確認する
- [ ] エラー・タイムアウトがあれば原因を調査・修正する
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-4.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `pre-01〜pre-03` + `qa-01〜qa-10` の計13シナリオが全件完了（エラーなし）
- 各シナリオの `workflow_details.json` に `read_sections` が記録されている

### #5: 全34シナリオ × 3 run ベンチマーク実行

**Purpose**: k=10・メタフィルタありの条件で全34シナリオを3 run実施し、crossrun-summary.md と quality-report.md を生成する

**Prerequisites**: #4

**Steps**:

- [ ] run-1: 全34シナリオ実行 → `HOW-TO-RUN.md` B-2（エラー回収）→ B-3（レポート生成）→ B-4（コミット）
- [ ] run-2: 同上
- [ ] run-3: 同上
- [ ] フェーズC-1: crossrun-summary.md 生成・コミット
- [ ] フェーズC-2: 閾値割れシナリオの裏付け調査（answer.md とナレッジの突き合わせ）
- [ ] フェーズC-3: quality-report.md 作成・コミット（現行ベースライン `20260616-1214-fullbench-classes-v6` との比較を含む）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-5.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `tools/benchmark/results/{date}-rag-k10-filter/` に run-1 / run-2 / run-3 の全34シナリオ結果が揃っている
- `crossrun-summary.md` と `quality-report.md` が生成されている
- `quality-report.md` に現行ベースライン（`20260616-1214-fullbench-classes-v6`）との比較が含まれている

### #6: 採用判定レポート作成

**Purpose**: 計測結果を総括し、必要に応じて追加計測を行い、RAG採用の可否を結論づける評価レポートを作成する

**Prerequisites**: #5

**Steps**:

- [ ] #5の結果を評価する（34シナリオ全パスかどうか）
- [ ] 必要に応じてk=20 / naive（フィルタなし）条件を追加計測する（設計書§7.2）
- [ ] 必要に応じてCohere Rerank 3.5を投入して再計測する（設計書§7.3 step 6）
- [ ] `docs/reports/rag/rag-evaluation-report.md` を作成する
  - 計測条件・結果サマリー
  - 現行エージェンティック検索との比較（精度・コスト・速度）
  - 語彙ギャップ分析（miss/partialシナリオの原因分析）
  - 明確なadopt/reject結論と理由
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-6.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `docs/reports/rag/rag-evaluation-report.md` が存在する
- レポートに現行比較（精度・コスト・速度）が含まれている
- レポートにadopt/rejectの結論が明記されている
- Issue #383のSuccess Criteriaが満たされている（v6ベンチ結果取得・評価レポート作成・adopt/reject結論）

# Decisions

（未記録）

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: 2026-06-25
- **Last completed**: none
- **Next**: #1 Docker環境構築とIndexingスクリプト実装（小規模動作確認まで）
- **Notes**: 現行ベースライン: `tools/benchmark/results/20260616-1214-fullbench-classes-v6/`。設計書: `docs/reports/rag/rag-nabledge-design.md`。
