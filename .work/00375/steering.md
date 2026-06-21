# Goal

Nabledge のコスト最適化について、アーキテクチャ観点（現方式 vs RAG 等）および単体最適化（サブエージェント化）の両面を事実ベースでフラットに評価し、有識者レビューに耐えるレポートを完成させる。

# Acceptance criteria

- [ ] アーキテクチャ観点で評価できている（cost-optimization-architecture.md）
- [ ] Nabledge単体で評価できている（cost-optimization-nabledge.md）
- [ ] 有識者レビューに対応済み（Recall@k実測でRAG評価を事実ベースに）

# Assumptions

- レポートの読み手: 有識者レビュアー + リーダー層（一般エンジニアレベルの前提知識）
- 品質基準: 事実【事実】/ 試算【試算】/ 推測【推測】をラベルで明示
- Bedrock Tokyo / Claude Sonnet 4.6 が前提

# Rules

- 推測でなく事実ベース（cost-evaluation-brief.md §5-2 のラベリング方針を遵守）
- 試算根拠を積み上げ式で示す
- RAG評価はRecall@k実測で裏付けてから結論を書く

# Tasks

See [tasks.md](tasks.md).

# State

Status: paused
Date: 2026-06-22
Last completed: エキスパート試算（3方式コスト比較）+ ベンチマーク分析（mustファイル・top-k期待値）
Next: Recall@k 事前検証スクリプト作成・実行
Notes: |
  作業ブランチ: 375-cost-optimization-docs（PR #376）
  タスクファイル: .work/00375/tasks.md

  現在の状況:
  - コスト最適化評価レポート2本 + 依頼書を docs/reports/ に追加済み
  - エキスパートレビュー9 Findings → 主要修正点特定済み
  - エキスパートによる3方式コスト試算完了:
    - 現状:  warm ¥80.6【事実】/ cold ¥265【試算】
    - サブ化: warm ¥28【試算】 / cold ¥53【試算】
    - RAG:   top-5 warm ¥9.5 〜 top-150 warm ¥45【試算】

  RAGのノックアウトファクター分析（期待値計算）:
  - 34シナリオ / 44 must / 22ファイル / 平均34KB・19.6セクション
  - libraries-tag.json = 166KB・51セクション → 81チャンク → 期待値top-40必要
  - 通常RAGのtop-kは3〜10 → 設計として成立しない可能性が高い
  - ただし「期待値計算」止まり → Recall@k実測で裏付けが必要

  次のアクション:
  1. python3 -c "import sentence_transformers" でライブラリ確認
  2. docs/reports/recall_at_k.py を作成・実行（Recall@k計算）
  3. 実測結果でレポート2本を更新

  レポート修正待ち項目:
  - cost-optimization-architecture.md: RAGコスト¥70.3→正しい試算、CAG却下理由修正、cache cold追加
  - cost-optimization-nabledge.md: 「精度は犠牲にしない」→「〔要実測確認〕」、サブ化コスト更新
