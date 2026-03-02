---
name: nabledge-5
description: Nablarch 5フレームワークの構造化知識ベース。バッチ処理、RESTful Webサービス、ハンドラ、ライブラリ等のNablarch機能について質問に回答する。コード分析も可能。
---

# Nabledge-5: Nablarch 5 Knowledge Base

## トリガー条件

以下のいずれかに該当する場合にこのスキルが呼び出される:

- Nablarch 5に関する質問
- Nablarchの機能、API、設定、パターンについての質問
- Nablarchを使ったバッチ処理、RESTful Webサービスの実装に関する質問
- Nablarchのハンドラ、ライブラリ、テストフレームワークに関する質問
- Nablarchを使った既存コードの分析

## ワークフロー振り分け

入力を解析し、以下のワークフローに振り分ける:

- 「質問」「知りたい」「教えて」「使い方」等 → workflows/qa.md
- 「コード分析」「構造を理解」等 → workflows/code-analysis.md
- 判定できない場合 → workflows/qa.md（デフォルト）

## 知識制約

**重要**: 回答は知識ファイル（knowledge/**/*.json）の情報のみに基づく。

- LLMの学習データ、外部Webサイト、一般知識の使用は禁止
- 知識ファイルにない情報は「この情報は知識ファイルに含まれていません」と明示する

## 知識ファイルのパス

- 知識ファイル: knowledge/{type}/{category-id}/*.json
- インデックス: knowledge/index.toon
- 閲覧用Markdown: docs/

## ワークフロー一覧

| ワークフロー | 役割 |
|---|---|
| workflows/qa.md | 質問応答 |
| workflows/code-analysis.md | コード分析・ドキュメント生成 |
| workflows/_knowledge-search.md | 知識検索（内部。qa.md, code-analysis.mdから呼び出される） |

## エラーハンドリング

- 知識が見つからない場合: 「この情報は知識ファイルに含まれていません」+ index.toonから関連エントリを提示
- LLM学習データでの補完は行わない
