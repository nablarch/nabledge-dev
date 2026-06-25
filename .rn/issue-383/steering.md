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

### #1: Docker環境構築とIndexingパイプライン実装

**Purpose**: Qdrant起動のDocker環境と、v6 JSON知識ファイルをQdrantにIndexingするスクリプトを実装する

**Prerequisites**: none

**Steps**:

- [ ] `tools/rag/` ディレクトリ構造を設計・作成する（`docker/`, `scripts/`, `tests/` サブディレクトリ）
- [ ] `tools/rag/docker/docker-compose.yml` を実装する（Qdrant起動、ストレージマウント）
- [ ] `tools/rag/scripts/index.py` を実装する（JSON→chunk→メタ付与→Cohere Embed→Qdrant）
  - section単位チャンク化（`title` + `content` を結合してembed、page `title` を前置）
  - メタデータ付与：`processing_type` / `category` / `page_id` / `section_id` / `title` / `level` / `class_names` / `linked_pages`（パスから機械導出）
  - `input_type=search_document` でCohere Embed v4 Bedrock呼び出し
- [ ] `tools/rag/tests/test_index.py` を実装する（チャンク化・メタ導出のユニットテスト）
- [ ] `docker compose up` でQdrant起動確認
- [ ] v6全件Indexing実行・完了確認（約9,376 sections）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-1.md`）
- [ ] QA expert review（subagent）
- [ ] language expert review（subagent）
- [ ] software-engineering expert review（subagent）
- [ ] user review

**Completion criteria**:

- `tools/rag/docker/docker-compose.yml` が存在し、`docker compose up` でQdrantが起動する
- `tools/rag/scripts/index.py` を実行するとv6全知識ファイルがQdrantにIndexingされる
- Qdrantコレクションに9,000件以上のpointが格納されている（設計書§2.2の9,376 sections相当）
- 各pointのmetadataに `processing_type` / `category` / `page_id` / `section_id` が含まれている
- `tools/rag/tests/test_index.py` のテストがすべてパスする

### #2: RAG版クエリエンジン実装

**Purpose**: 質問をCohere Embed v4でベクトル化し、Qdrant top-k検索でsectionを取得するクエリエンジンを実装する

**Prerequisites**: #1

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
- [ ] 1シナリオ（`pre-01`）で動作確認（`workflow_details.json` の `read_sections` に正しい `path.json:sN` 形式が含まれる）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-2.md`）
- [ ] QA expert review（subagent）
- [ ] language expert review（subagent）
- [ ] software-engineering expert review（subagent）
- [ ] user review

**Completion criteria**:

- `tools/rag/scripts/run_rag_qa.py --scenario-ids pre-01` が終了コード0で完了する
- 出力ディレクトリに `workflow_details.json` / `answer.md` / `metrics.json` / `evaluation.json` が揃う
- `workflow_details.json` の `read_sections` が `path.json:sN` 形式で記録されている
- `tools/rag/tests/test_query.py` のテストがすべてパスする

### #3: E2Eベンチマーク実行（k=10, filter, 3 run）

**Purpose**: k=10・メタフィルタありの条件で34シナリオ × 3 runのE2Eベンチマークを実施する（設計書§7.2の第1計測条件）

**Prerequisites**: #2

**Steps**:

- [ ] `HOW-TO-RUN.md` のフェーズA（動作確認）を実施する（RAG版 run_rag_qa.py で pre-01 確認）
- [ ] フェーズB × 3 run 実行・レポート生成・コミット（ラベル: `{date}-rag-k10-filter`）
- [ ] フェーズC-1: crossrun-summary.md 生成・コミット
- [ ] フェーズC-2: 閾値割れシナリオの裏付け調査
- [ ] フェーズC-3: quality-report.md 作成・コミット（現行ベースライン `20260616-1214-fullbench-classes-v6` との比較を含む）
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-3.md`）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- `tools/benchmark/results/{date}-rag-k10-filter/` に run-1 / run-2 / run-3 の全シナリオ結果が揃っている
- `crossrun-summary.md` と `quality-report.md` が生成されている
- `quality-report.md` に現行ベースラインとの比較が含まれている

### #4: 追加計測と採用判定レポート作成

**Purpose**: 必要に応じてk=20・naive（フィルタなし）条件を追加計測し、RAG採用の可否を判定する評価レポートを作成する

**Prerequisites**: #3

**Steps**:

- [ ] #3の結果を評価する（採用基準: 34シナリオ全パス = ゼロディフェクト要件）
- [ ] 必要に応じてk=20 / naive条件を追加計測する（設計書§7.2）
- [ ] 必要に応じてCohere Rerank 3.5を投入して再計測する（設計書§7.3 step 6）
- [ ] `docs/reports/rag/rag-evaluation-report.md` を作成する
  - 計測条件・結果サマリー
  - 現行エージェンティック検索との比較（精度・コスト・速度）
  - 語彙ギャップ分析（miss/partialシナリオの原因分析）
  - 明確なadopt/reject結論と理由
- [ ] self-check（OK/NG per completion criterion、記録: `.rn/issue-383/checks/task-4.md`）
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
- **Next**: #1 Docker環境構築とIndexingパイプライン実装
- **Notes**: 現行ベースライン: `tools/benchmark/results/20260616-1214-fullbench-classes-v6/`。設計書: `docs/reports/rag/rag-nabledge-design.md`。
