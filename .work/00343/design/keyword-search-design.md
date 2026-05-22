# キーワード検索 設計書

**Status**: Approved
**Date**: 2026-05-22 (updated: terms.json → full-text scan)

## 目的

既知の技術用語でセクションを確実にヒットさせる検索方式を提供する。コード分析、レビュー、影響調査で使用する。

## 位置づけ

```
code-analysis.md
  └── keyword-search.md     ← ここ
        └── keyword-search.sh
              └── knowledge/ 全JSONファイルを直接スキャン
```

semantic-searchとは独立した公開ワークフロー。出力インタフェース（pointer JSON）は共通。

## 背景と変更

当初は事前生成したterms.json（term→section_idの逆引きマップ）を使用していた。しかし:

- terms.jsonはterm抽出ルールに合致するもののみ索引するため、ルールから漏れたキーワードが取りこぼされる構造的問題があった
- ルール追加では根本解決しない（次の取りこぼしが必ず出る）
- 全文スキャンは約1.6ms/クエリでterms.json読み込み（229ms）より高速

ベンチマーク結果: terms.json方式 vs 全文スキャン
- impact-09: recall=0.00 → 1.00（取りこぼし解消）
- その他11シナリオ: recall変化なし

## 方式

### 概要

```
キーワード → keyword-search.sh → knowledge/全JSONをスキャン → セクションIDリスト
```

knowledge/配下の全JSONファイルを直接スキャンする。LLMは使わない。

### keyword-search.sh

```
入力: キーワード（1つ以上、各2文字以上）
出力: JSON — category > page > section 階層

アルゴリズム:
1. knowledge/配下の全JSONファイルを走査
2. no_knowledge_content: trueのファイルはスキップ
3. 各ファイルについて、ページレベルANDフィルタ:
   - 全キーワードが何らかのセクションのtitleまたはcontentにヒットするファイルのみ残す
4. セクションレベルOR収集:
   - 有効ファイルの各セクションについて、いずれかのキーワードがtitleまたはcontentにヒットするセクションを収集
5. カテゴリ別→ページ別に階層化して出力（結果数制限なし）
```

マッチングはcase-insensitive部分一致。2文字未満のキーワードはノイズ防止のため無視する。`KNOWLEDGE_DIR`環境変数でknowledgeディレクトリを外部から指定可能（テスト用）。

### keyword-search.md（ワークフロー）

```
入力: キーワード配列

出力: pointer JSON（semantic-searchと共通インタフェース）
{
  "results": [
    {"file": "component/libraries/universal-dao.json", "section_id": "s1", "relevance": "partial"},
    ...
  ]
}

1. keyword-search.shを実行し、階層JSONを取得
2. 階層JSONをpointer JSONに変換して返す
   - 各セクションエントリの section_id（"file:sid"形式）を最後の":"で分割し、fileとsidに分解
   - {"file": file, "section_id": sid, "relevance": "partial"} を生成
   - (file, section_id)で重複排除
```

LLMの判断は不要。スクリプト結果をpointer JSONに変換して返す。relevanceは常に"partial"（high/lowなし）。

## テスト

LLM不使用のためシミュレーション不要。pytest統合テスト（26テスト）で評価完結:

- **基本マッチ**: 完全一致、case-insensitive、部分一致、日本語、略語
- **複数キーワードAND**: 同一ページヒット、共通ページなし、AND絞り込み
- **最小長**: 1文字除外、2文字受理
- **no_knowledge_content除外**: フラグtrueのファイルは結果に含まれない
- **出力形式**: JSON構造、カテゴリグルーピング、ソート順
- **全文スキャン**: terms.json不要、セクションcontent/titleマッチ
- **エラー**: 引数なし、マッチなし、空ディレクトリ
