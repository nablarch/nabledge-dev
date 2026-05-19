# Nabledge 検索アーキテクチャ設計

**Status**: Draft
**Date**: 2026-05-15

## フェーズ

本設計は2フェーズで実現する。

**フェーズA（部品実装+部品ベンチマーク）**:
- 新検索の各コンポーネント設計・実装（`tools/benchmark/components/prompts/`にプロンプト、`tools/benchmark/components/scripts/`にスクリプト）
- 部品単位のベンチマーク（`simulate_*.py`で各コンポーネントを個別評価）
- RBKC変更は要件設計のみ
- 現行検索は一切変更しない

**フェーズB（RBKC変更+新検索デプロイ+E2Eベンチマーク）**:
- RBKCの変更（index.md生成、terms.json出力、セキュリティチェックExcel修正）
- 新検索のスキルへのデプロイ（ワークフロー、アセット）
- 現行検索のE2Eベンチマーク（v6のみ）
- 新検索のE2Eベンチマーク（v6のみ）
- 現行vs新の比較、現行以上になるまで改善
- 残りバージョンへの展開

## 検索要件

精度最優先。SoRシステム（金融・決済）の知識検索であり、以下の2条件を満たすこと。

**回答精度**: 質問の意図を踏まえて、最低限必須の知識が回答に含まれていること。

**ハルシネーション防止**: 知識ベースにない捏造が回答に含まれないこと。

## ベンチマーク要件

回答精度・ハルシネーション防止はLLMで自動判定し、知識ベースとのマッチで評価する。ただしLLM判定は知識にマッチしないものをNGにする傾向があるため、人間が最終評価する。

実行時間とコストはベンチマークで計測し報告する。検索要件としては扱わない。

具体的な計測方法と閾値はベンチマーク設計で定義する。

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
| keyword-search.md | キーワード（1つ以上） | スクリプトによる機械的マッチ | コード分析（セクションポインタ取得） |
| semantic-search.md | 自然言語の質問文、ヒアリング結果（hearing_answer） | AIによるインデックスからのセクション選定 | 質問 |

keyword-searchは既知の用語で確実にヒットさせる（precision重視）。semantic-searchは語彙ギャップを超えて関連セクションを発見し、重要度（high/partial）を付与する（recall重視）。コード分析はStep 1でNablarchクラス名が確定するため、keyword-searchのみを使う。

---

## ディレクトリ構成

### フェーズA: 部品実装+部品ベンチマーク

フェーズAでは現行スキルを一切変更しない。部品（プロンプト・スクリプト）はすべて `tools/benchmark/` 内に配置する。

```
tools/benchmark/
  components/
    prompts/
      hearing-classify.md             ← ヒアリング分類プロンプト
      hearing-extract.md              ← ヒアリング抽出プロンプト
      semantic-search-stage1.md       ← 意味検索Stage1プロンプト
      semantic-search-stage2.md       ← 意味検索Stage2プロンプト
      answer.md                       ← 回答生成プロンプト
      verify.md                       ← 根拠検証プロンプト
    scripts/
      keyword-search.sh              ← キーワード検索スクリプト
      read-sections.sh               ← セクション本文取得
  prompts/
    c-claim-judge.md                  ← 回答精度LLM判定プロンプト
    hallucination-judge.md            ← ハルシネーション判定プロンプト
  scripts/
    simulate_hearing.py               ← ヒアリング部品ベンチマーク
    simulate_semantic_search.py       ← 意味検索部品ベンチマーク
    simulate_answer.py                ← 回答生成部品ベンチマーク
    simulate_verify.py                ← 検証部品ベンチマーク
    simulate_answer_verify.py         ← 回答+検証部品ベンチマーク
    run.py                            ← 部品チェーン実行（hearing→search→answer）
    evaluate.py                       ← 評価（ルールベース+LLM判定）
    report.py                         ← レポート生成
    generate_index.py                 ← index.md生成（ベンチマーク用）
  scenarios/
    qa.json                           ← QAシナリオ（15件）
    keyword-search.json               ← キーワード検索シナリオ（12件）
```

- `components/` はフェーズBでスキルにデプロイする部品。ベンチマーク内で開発・評価する
- `prompts/` はベンチマーク専用（LLM判定用）。スキルにはデプロイしない
- `scripts/` はベンチマーク実行インフラ。スキルにはデプロイしない

### フェーズB: RBKC変更+スキルデプロイ+E2Eベンチマーク

フェーズAの部品をスキルにデプロイし、RBKC変更を実施する。

```
.claude/skills/nabledge-6/
  knowledge/
    {category}/                       ← 知識ファイル（RBKC生成、カテゴリ別サブディレクトリ）
      about/
      assets/
      check/
      component/
      development-tools/
      guide/
      processing-pattern/
      releases/
      setup/
    index.md                          ← セクション目次（RBKC生成）
    terms.json                        ← term→section_idマップ（RBKC生成）
  workflows/
    qa.md                             ← 質問応答オーケストレーション
    qa/                               ← qa.md が参照するサブワークフロー（コロケーション）
      hearing.md                      ← ヒアリング（LLMプロンプトをインライン）
      answer.md                       ← 回答生成（LLMプロンプトをインライン）
      verify.md                       ← 根拠検証（LLMプロンプトをインライン）
    keyword-search.md                 ← キーワード検索（公開）
    semantic-search.md                ← 意味検索（公開、LLMプロンプトをインライン）
    code-analysis.md                  ← コード分析
    code-analysis/                    ← code-analysis.md が参照するテンプレート（コロケーション）
      template.md                     ← コード分析テンプレート
      template-guide.md               ← テンプレートガイド
      template-examples.md            ← テンプレート例
  scripts/
    keyword-search.sh                 ← components/scripts/ からデプロイ
    read-sections.sh                  ← components/scripts/ からデプロイ
  assets/                             ← 空（プロンプトはワークフローMDにインライン化）

tools/rbkc/
  scripts/create/
    index.py                          ← index.md生成（index.toon → index.mdへ変更）
    terms.py                          ← terms.json生成
```

**ファイル配置の原則（コロケーション）**:
- ワークフローとその依存ファイルは同一ディレクトリまたは直下のサブディレクトリに配置する
- LLMへのプロンプト指示はワークフローMD（`qa/hearing.md`等）にインライン化する（`assets/`参照なし）
- `qa/`サブディレクトリは`qa.md`専用。`code-analysis/`サブディレクトリは`code-analysis.md`専用

- keyword-search.md、semantic-search.mdは公開ワークフロー。PJ側で独自ワークフローから直接呼べる
- qa/配下もベンチマークから個別に呼べるよう公開
- フェーズAの `components/` をフェーズBでスキルにデプロイする
