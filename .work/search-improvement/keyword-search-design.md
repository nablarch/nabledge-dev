# キーワード検索 設計書

**Status**: Draft
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
  "version": "1",
  "terms": {
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
6. プロパティ名（ドット区切り: `nablarch.core.validation`）
7. 複合キーワード（ハイフン・スネーク区切り: `use-token`, `batch_update`）

**除外対象:**
- 一般的な日本語（助詞、動詞、一般名詞）
- 一般的な英語（the, is, for, etc.）
- 1文字のトークン
- HTML/RSTマークアップ残骸

### keyword-search.sh

```
入力: キーワード（1つ以上）
出力: pointer JSON（relevance降順）

アルゴリズム:
1. terms.jsonを読み込む
2. 各入力キーワードについて:
   a. terms.jsonで完全一致するtermを検索
   b. 一致しなければ、大文字小文字無視で検索
   c. それでも一致しなければ、部分一致で検索（ただし入力キーワードが5文字以下の場合は部分一致をスキップ。短いキーワードの部分一致はノイズが多すぎるため）
3. ヒットしたsection_idをスコアリング:
   - 各セクションのスコア = マッチしたキーワード数
4. スコア降順でソート
5. 上位30件をpointer JSON形式で出力
```

3段階マッチ（完全→大小無視→部分）により、正確なキーワードほど優先的にヒットする。

### keyword-search.md（ワークフロー）

```
入力: キーワード配列

1. keyword-search.shを実行し、pointer JSONを取得
2. pointer JSONをそのまま返す
```

LLMの判断は不要。スクリプトの結果をそのまま返すパススルーワークフロー。

## ベンチマーク

### 評価方法

12件の既存keyword-searchシナリオで評価。keyword-search.shの出力にmustセクションが含まれているかを検証。

### メトリクス

- **must recall**: mustセクションのヒット率（target: 100%）
- **precision@15**: top 15にmustセクションが含まれる率
- **ランク**: mustセクションの出力順位

### シミュレーション

LLM不使用のためシミュレーション不要。スクリプト単体テストで評価完結。

## 実装計画

1. terms.json生成（RBKCステップ追加）
2. keyword-search.sh実装
3. keyword-search.md作成
4. ベンチマーク実行
