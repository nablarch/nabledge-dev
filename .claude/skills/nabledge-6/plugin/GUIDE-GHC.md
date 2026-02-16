# GitHub Copilot 利用ガイド

Nabledge-6を GitHub Copilot で使用するためのガイドです。

## 前提条件

- **WSL または GitBash 環境**
  - VS Code のターミナルを使用する場合は、ターミナルを WSL または GitBash に設定してください
  - PowerShell や Command Prompt では動作しません
- プロジェクトディレクトリで作業していること

## インストール

プロジェクトルートで以下のコマンドを実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

実行後、`.claude` ディレクトリがプロジェクトに作成されます。

### チーム共有

`.claude` ディレクトリをGitにコミット・プッシュしてください。チームメンバーも同じスキルを利用できるようになります。

### 注意事項

- セットアップスクリプトは必要に応じて `jq` コマンドを自動インストールします（Linux/WSL/GitBash環境）
- macOSでは手動インストールが必要です: `brew install jq`

### 環境変数でカスタマイズ (オプション)

リポジトリやブランチをカスタマイズする場合:

```bash
# テストブランチを使用する場合
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh -o setup.sh
NABLEDGE_BRANCH=test-to bash setup.sh

# フォーク版を使用する場合
curl -sSL https://raw.githubusercontent.com/mycompany/nabledge-fork/custom/setup-6-ghc.sh -o setup.sh
NABLEDGE_REPO=mycompany/nabledge-fork NABLEDGE_BRANCH=custom bash setup.sh
```

## 使い方

### 基本的な使い方

エディタで以下のようにスキルを呼び出します：

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

セットアップスクリプトを再実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

更新後、`.claude` ディレクトリの変更をGitにコミット・プッシュしてください。
