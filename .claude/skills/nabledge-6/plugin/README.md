# Nabledge-6

Nablarch 6のAI支援開発スキルです。

## 機能

Nabledge-6は **知識** と **ワークフロー** の2種類の機能を提供します。

### 知識

Nablarch 6のドキュメントやベストプラクティスをエージェントが参照できるようにします。

現在カバーしている領域:

- バッチ処理の基礎知識
- データベースアクセスの実装方法
- テスティングフレームワークの使い方
- セキュリティチェックリスト

今後追加予定の領域:

- RESTful Webサービス
- ハンドラの詳細仕様

### ワークフロー

Nablarchの知識を活用した開発支援ワークフローを提供します。

現在提供しているワークフロー:

- **コード分析**: Nablarchの観点からプロジェクトコードを分析し、改善提案を行う

今後追加予定のワークフロー:

- **影響調査**: 変更による影響範囲をNablarchの構造を踏まえて調査
- **コードレビュー**: Nablarchの規約やベストプラクティスに基づくレビュー

注：評価版のため、知識・ワークフローともにカバー範囲は限定的です。フィードバックをもとに拡充していきます。

## インストール

### Claude Code

#### 個人用インストール

```bash
# マーケットプレイスを追加
/plugin marketplace add nablarch/nabledge

# プラグインをインストール
/plugin install nabledge-6@nabledge
```

#### チーム設定（推奨）

プロジェクトメンバー全員で利用する場合は、プロジェクトスコープでインストール：

```bash
# マーケットプレイスを追加
/plugin marketplace add nablarch/nabledge

# プロジェクトスコープでインストール
/plugin install nabledge-6@nabledge --scope project
```

または、`.claude/settings.json` に直接記述：

```json
{
  "extraKnownMarketplaces": [
    {
      "name": "nabledge",
      "source": "https://github.com/nablarch/nabledge.git"
    }
  ],
  "enabledPlugins": {
    "nabledge-6@nabledge": {
      "enabled": true
    }
  }
}
```

このファイルをGitにコミットすると、チームメンバーがリポジトリをクローンした際に自動的にプラグインのインストールが促されます。

### GitHub Copilot (WSL / GitBash)

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/.claude/skills/nabledge-6/scripts/setup.sh | bash
```

## 使い方

### 基本的な使い方

```bash
/nabledge-6
```

スキルを起動し、対話的にNablarchに関する質問や、コード分析を行うことができます。

### 知識検索

```bash
/nabledge-6 "バッチ処理の実装方法を教えて"
```

Nablarch 6のドキュメントやベストプラクティスから知識を検索し、回答を得ることができます。質問は日本語でも英語でも可能です。

### コード分析

```bash
/nabledge-6 code-analysis
```

現在のプロジェクトのコードをNablarchの観点から分析します。Actionクラス、ハンドラ構成、データベースアクセスパターンなどを評価し、改善提案を提供します。

## バージョンアップ

### Claude Code

マーケットプレイスは起動時に自動更新されます。手動で更新する場合：

```bash
# マーケットプレイスを更新（最新版を取得）
/plugin marketplace update nabledge

# 特定バージョンを指定する場合
/plugin marketplace add nablarch/nabledge#v0.2
```

プラグインを再インストール：

```bash
/plugin install nabledge-6@nabledge
```

### GitHub Copilot (WSL / GitBash)

セットアップスクリプトを再実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/.claude/skills/nabledge-6/scripts/setup.sh | bash
```

特定バージョンを指定する場合：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/v0.2/.claude/skills/nabledge-6/scripts/setup.sh | bash
```
