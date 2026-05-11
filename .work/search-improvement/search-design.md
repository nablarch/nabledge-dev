# Nabledge 検索アーキテクチャ設計

**Status**: Draft
**Date**: 2026-05-11

## 要件

精度最優先。SoRシステム（金融・決済）の知識検索であり、以下の2条件を満たすこと。

**回答精度**: 質問の意図を踏まえて、最低限必須の知識が回答に含まれていること。

**ハルシネーション防止**: 知識ベースにない捏造が回答に含まれないこと。

どちらもLLMで機械的に判定し、知識ベースとのマッチで評価する。ただしLLM判定は知識にマッチしないものをNGにする傾向があるため、人間が最終評価する。具体的な計測方法と閾値はベンチマーク設計で定義する。

実行時間とコストはベンチマークで計測し報告する。要件としては扱わない。

---

## 前提・制約

1. **LLMがフロー制御** — CC（Claude Code）とGHC（GitHub Copilot）の両方に対応するため、検索フローはLLMが制御する構成とする
2. **知識ファイル・インデックスはすべてルールベース生成** — 手動ヒント等を入れるとイタチごっこになり汎用性能が出ないため、RBKCによる機械的生成のみ
3. **要件の2条件（回答精度・ハルシネーション防止）は必須** — これを満たさない設計変更は採用しない

---

## UX

ユーザーから見た体験は以下の2パターン。

**パターン1: 具体的な質問（ヒアリングなし）**
```
User: 「UniversalDaoの使い方」
System: （検索+回答）
        UniversalDaoでは...（引用付き回答）
```

**パターン2: 曖昧な質問（ヒアリングあり）**
```
User: 「入力チェックのやり方」
System: 対象のアプリケーション種別を教えてもらえますか？
        - ウェブアプリケーション（HTML画面のフォーム入力）
        - RESTful API（JSONリクエストのバリデーション）
User: 「RESTです」
System: （検索+回答）
        REST APIの入力チェックでは...（引用付き回答）
```

ヒアリングで質問を十分に絞り込んでから意味検索に渡す。意味検索の精度はヒアリングの質に依存する。

---

## アーキテクチャ

### ワークフロー構成

```
qa.md（質問応答オーケストレーション）
  ├── qa/hearing.md         ヒアリング
  ├── semantic-search.md    意味検索 → セクションIDリスト
  ├── read-sections.sh      セクション本文取得
  ├── qa/answer.md          回答生成
  └── qa/verify.md          根拠検証

code-analysis.md（コード分析）
  ├── keyword-search.md     キーワード検索 → セクションIDリスト
  ├── read-sections.sh      セクション本文取得
  └── レポート生成
```

### 知識検索の2経路

知識検索は2つの独立した公開ワークフローとして提供する。出力インタフェース（セクションIDリスト）は共通。

| ワークフロー | 入力 | 方式 | 利用想定 |
|------------|------|------|--------|
| keyword-search.md | キーワード（1つ以上） | スクリプトによる機械的マッチ | コード分析、レビュー、影響調査 等 |
| semantic-search.md | 自然言語の質問文 | AIによるインデックスからのセクション選定 | 質問 |

keyword-searchは既知の用語で確実にヒットさせる（precision重視）。semantic-searchは語彙ギャップを超えて関連セクションを発見する（recall重視）。

---

## ディレクトリ構成

```
.claude/skills/nabledge-6/
  knowledge/
    *.json                            ← 知識ファイル（RBKC生成）
    index.md                          ← セクション目次（RBKC生成）
    terms.json                        ← term→section_idマップ（RBKC生成）
  workflows/
    qa.md                             ← 質問応答オーケストレーション（変更）
    qa/
      hearing.md                      ← ヒアリング
      answer.md                       ← 回答生成
      verify.md                       ← 根拠検証
    keyword-search.md                 ← キーワード検索（公開）
    semantic-search.md                ← 意味検索（公開）
    code-analysis.md                  ← コード分析（軽微変更）
  scripts/
    keyword-search.sh                 ← キーワード検索スクリプト（旧full-text-search.sh）
    annotate-index.sh                 ← semantic-searchのStep 1で使用。index.mdに★注釈を付与
    read-sections.sh                  ← セクション本文取得（既存）
  assets/
    hearing-prompt.md                 ← ヒアリング判定LLMプロンプト
    c-claim-judge-prompt.md           ← C-claim判定LLMプロンプト

tools/rbkc/
  scripts/create/
    step{N}_create_index_md.py        ← index.md生成
    step{N}_create_terms.py           ← terms.json生成
```

- keyword-search.md、semantic-search.mdは公開ワークフロー。PJ側で独自ワークフローから直接呼べる
- qa/配下もベンチマークから個別に呼べるよう公開
- プロンプトはassets/に配置。ワークフローMDから参照する
