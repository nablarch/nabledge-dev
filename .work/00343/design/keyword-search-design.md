# キーワード検索 設計書

**Status**: Approved
**Date**: 2026-05-15

## 目的

既知の技術用語でセクションを確実にヒットさせる検索方式を提供する。コード分析、レビュー、影響調査で使用する。

## 位置づけ

```
code-analysis.md
  └── keyword-search.md     ← ここ
        └── keyword-search.sh
              └── knowledge/terms.json
```

semantic-searchとは独立した公開ワークフロー。出力インタフェース（pointer JSON）は共通。

## 現状の問題

現行`full-text-search.sh`はセクションのtitle+contentに対するOR部分一致検索。12件のベンチマークシナリオでmustセクションがtop 15に入らない（review-01: 0/3 must）。

原因: OR一致でスコアが分散し、キーワードを偶然多く含むGetting Startedページが上位に来る。

## 方式

### 概要

```
キーワード → keyword-search.sh → terms.json照合 → セクションIDリスト
```

事前生成したterm→section_idマップ（terms.json）をスクリプトで照合する。LLMは使わない。

### terms.json

RBKC生成。知識ファイルの各セクションからtechnical termを抽出し、term→section_idの逆引きマップを構築する。

```json
{
  "UniversalDao": [
    "component/libraries/libraries-universal-dao.json:s1",
    "component/libraries/libraries-universal-dao.json:s14",
    "component/libraries/libraries-universal-dao.json:s15"
  ],
  "batchUpdate": [
    "component/libraries/libraries-universal-dao.json:s14"
  ],
  "ドメインバリデーション": [
    "component/libraries/libraries-bean-validation.json:s9"
  ]
}
```

### term抽出ルール

各セクションのtitleとcontentから以下を抽出する。

**抽出対象:**
1. Javaクラス名（CamelCase: `UniversalDao`, `BatchAction`）
2. メソッド名（camelCase: `batchUpdate`, `findAll`）
3. アノテーション名（`@Valid`, `@Published`）
4. 日本語技術用語（セクションタイトルから抽出）:
   - セクションタイトル全体をtermとして登録
   - 末尾の一般動詞パターン（`を使う`, `を行う`, `する`, `について`, `のやり方`等）を除去した形もtermとして登録
   - 例: 「ドメインバリデーションを使う」→ `ドメインバリデーションを使う` + `ドメインバリデーション`
5. 英語略語（全大文字2文字以上: `CORS`, `CSP`, `CSRF`）
6. プロパティ名（ドット区切り3セグメント以上: `nablarch.core.validation`。2セグメント（`nablarch.core`）はクラス名等と誤検出するため除外）
7. 複合キーワード（ハイフン区切り: `use-token`, `content-type`）

**除外対象:**
- 一般的な日本語（助詞、動詞、一般名詞）
- 一般的な英語（the, is, for, etc.）
- 1文字のトークン
- HTML/RSTマークアップ残骸
- 高頻度term（section_df ≥ 7%のtermはストップリストとして除外。多くのセクションに出現するtermは検索ノイズになるため）

### keyword-search.sh

```
入力: キーワード（1つ以上、各2文字以上）
出力: JSON — category > page > section 階層

アルゴリズム:
1. terms.jsonを読み込む
2. 各キーワードについて:
   - case-insensitive部分一致でterms.jsonを検索
   - マッチしたtermのsection_idを収集
3. ページレベルAND:
   - 全キーワードがヒットしたページのみ残す
4. セクションレベルOR:
   - 有効ページ内の全ヒットセクションを返す
5. カテゴリ別→ページ別に階層化して出力（結果数制限なし）
```

2文字未満のキーワードはノイズ防止のため無視する。`no_knowledge_content: true`のファイルは除外する。`KNOWLEDGE_DIR`環境変数でknowledgeディレクトリを外部から指定可能（テスト用）。

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

LLM不使用のためシミュレーション不要。pytest統合テスト（20テスト）で評価完結:

- **基本マッチ**: 完全一致、case-insensitive、部分一致、日本語、略語
- **複数キーワードAND**: 同一ページヒット、共通ページなし、AND絞り込み
- **最小長**: 1文字除外、2文字受理
- **no_knowledge_content除外**: フラグtrueのファイルは結果に含まれない
- **出力形式**: JSON構造、カテゴリグルーピング、ソート順
- **エラー**: 引数なし、マッチなし、terms.json欠如
