# Tasks: Nabledge コスト最適化評価レポート作成

**Branch**: 375-cost-optimization-docs
**Updated**: 2026-06-22

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
- [x] PR作成: #376
- [x] スコープ確定: ドキュメント追加のみ（Recall@k実測・レポート書き直しは対象外）
