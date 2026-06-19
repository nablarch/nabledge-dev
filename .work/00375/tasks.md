# Tasks: Nabledge コスト最適化評価レポート作成

**Branch**: 375-cost-optimization-docs
**Updated**: 2026-06-19

## In Progress

### Recall@k 事前検証スクリプト作成・実行

RAGがNablarchの知識ファイルに対してtop-kでmustセクションをカバーできるかを
機械的に検証する。

**Purpose**: RAGのノックアウトファクターを「期待値計算」でなく「実測」で示す。

**Steps**:
- [ ] `sentence-transformers` がインストール済みか確認 (`python3 -c "import sentence_transformers"`)
  - 入っていなければインストールするかユーザーに確認
- [ ] スクリプト作成: `docs/reports/recall_at_k.py`
  - docs/ MD 936ファイルを512トークンでチャンク化
  - ベンチマーク34シナリオのinputをクエリとして埋め込み
  - 各クエリのmustセクションがtop-kに入るか計算（k=5,10,20,40,87,110）
  - Recall@k（全mustが取れたシナリオ割合）を出力
- [ ] 実行・結果確認
- [ ] 結果をレポートに反映

**Materials**:
- クエリ: `tools/benchmark/scenarios/qa.json` の `when.input`（34シナリオ）
- 正解: `then.must[].section`（ファイル名:セクションID）
- コーパス: `.claude/skills/nabledge-6/` 配下の `docs/*.md`（936ファイル）
- mustファイル一覧と規模は調査済み（22ファイル、平均34KB・19.6セクション）

---

## Not Started

### レポート書き直し（cost-optimization-architecture.md / cost-optimization-nabledge.md）

Recall@k実測結果とエキスパート試算を踏まえ、2本のレポートを更新する。

**変更内容**:
- `cost-optimization-architecture.md`:
  - RAGコストを¥70.3（誤）→ 正しい試算（top-k別: ¥9〜¥48）に修正
  - RAGのノックアウトファクターをRecall@k実測で裏付け
  - cache cold/warm の両シナリオを追加
  - CAG却下理由を修正（「分割は事前に対象を定められない」を削除）
- `cost-optimization-nabledge.md`:
  - 「精度は犠牲にしない」→「〔要実測確認〕」に修正
  - サブ化コスト試算をオーバーヘッド込みで更新（warm ¥28 / cold ¥53）

---

## Done

- [x] ブランチ作成: `cost-optimization-docs`
- [x] ファイルリネーム（日本語→英語）: `cost-optimization-architecture.md`, `cost-optimization-nabledge.md`, `cost-evaluation-brief.md`
- [x] サブエージェント設計修正（1サブ連続実行 → メインがオーケストレーター）— commit `02a954d47`
- [x] エキスパートレビュー実施（Prompt Engineer / RAG / AI Engineering）— 9 Findings
- [x] エキスパート試算（3方式: 現状 / サブ化 / RAG）
  - 現状: warm ¥80.6【事実】/ cold ¥265【試算】
  - サブ化: warm ¥28【試算】/ cold ¥53【試算】
  - RAG: top-5 warm ¥9.5〜 top-150 warm ¥45【試算】
- [x] ベンチマーク分析（mustファイル構造・top-k必要数の期待値計算）
  - 34シナリオ / 44 must / 22ファイル / 平均34KB・19.6セクション
  - top-40〜110が期待値ラインだが通常RAGはtop-3〜10
- [x] PR作成: #374
