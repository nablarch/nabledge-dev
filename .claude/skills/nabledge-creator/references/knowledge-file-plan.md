# Knowledge File Plan

生成対象の知識ファイルとソースドキュメントの対応方針。

## ソース情報

### nablarch-document/en/ (動的スキャン対象)

`.lw/nab-official/v{version}/nablarch-document/en/`配下の全てのRSTファイルが対象。

- ファイルの増減に自動対応
- マッピングファイル (mapping-v{version}.md) から動的に取得
- 個別ファイルリストは不要（増減時のメンテナンス不要）

### 追加ソース (明示的対象)

nablarch-document/en/以外のソースを明示的にリスト:

#### Sample_Project/

- `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
  - Type: check
  - Category: security-check
  - Target: check/security-check/Nablarch機能のセキュリティ対応表.xlsx

#### Nablarch-system-development-guide/

- `en/Nablarch-system-development-guide/docs/nablarch-patterns/*.md`
  - Type: guide
  - Category: nablarch-patterns
  - 各MDファイルが個別の知識ファイルに対応

## 統合パターン

知識ファイルとマッピング行の対応関係:

| 知識ファイルの種類 | マッピング行との関係 | 説明 |
|---|---|---|
| 処理方式 (processing-pattern) | N:1 | 同じCategory IDのprocessing-pattern行を統合 |
| ハンドラ (handlers) | 1:1 | 各RSTファイルが個別の知識ファイル |
| ライブラリ (libraries) | 1:1または N:1 | 基本は1:1、サブ機能別ファイルならN:1 |
| ツール (tools) | N:1 | 関連ツールをグループ化 |
| アダプタ (adapters) | 1:1 | 各アダプタが個別の知識ファイル |
| チェック (check) | 1:1 | 各チェック資料が個別の知識ファイル |
| ガイド (guide) | 1:1 | 各ガイドが個別の知識ファイル |
| リリースノート (release) | 特殊 | バージョン別に1ファイル |
| 概要 (overview) | 特殊 | カテゴリの全体概要 |

## 知識ファイル生成方法

### 1. マッピングファイルから取得

`mapping-v{version}.md`から以下を取得:
- Source Path (RSTファイルパス)
- Title (英語・日本語)
- Type, Category ID, Processing Pattern
- Target Path (知識ファイルパス)
- Official URL

### 2. 統合パターンの適用

- **1:1パターン**: 各マッピング行から1つの知識ファイル生成
- **N:1パターン**: 複数のマッピング行を統合して1つの知識ファイル生成
  - 例: processing-pattern/jakarta-batch/*.json
  - 統合基準: Category ID、Processing Pattern等

### 3. ソースRSTの読込

`.lw/nab-official/v{version}/`配下からSource Pathを元にRSTファイルを読込:
- 英語RSTを優先
- 英語が存在しない場合は日本語RST

### 4. 知識ファイル生成

RSTの内容から以下を抽出:
- purpose (目的・概要)
- usage (使い方)
- configuration (設定方法)
- examples (コード例)
- notes (注意事項)
- L1/L2/L3キーワード (検索用)

## 動的スキャンのメリット

### ファイル増減への自動対応

- Nablarch公式ドキュメントにRSTファイルが追加されても、マッピング生成時に自動検出
- RSTファイルが削除されても、マッピングから自動除外
- knowledge-file-plan.mdの更新不要

### メンテナンス負荷の削減

- 個別ファイルリスト (2000+行) の管理不要
- バージョン間の差分管理が容易
- 統合パターンとソース情報のみ管理

### v5/v6互換性

- 同じ方針でv5, v6両方に対応
- バージョン固有の情報は`{version}`変数で吸収
- 追加ソースのみバージョン別に管理（必要に応じて）

## 注意事項

### 除外ファイル

以下は知識ファイル生成対象外（マッピング時に除外）:

- index.rst (ディレクトリインデックス)
- getting_started/*.rst (チュートリアル系)
- 一部の概念説明ファイル（マッピング除外リストで管理）

除外基準は`.claude/skills/nabledge-creator/references/classification.md`で定義。

### 特殊ケース

- **リリースノート**: releases/配下のRSTを統合して1つの知識ファイル
- **overview.json**: 各カテゴリの全体概要（自動生成または手動作成）
- **index.json**: カテゴリのインデックス（自動生成）
