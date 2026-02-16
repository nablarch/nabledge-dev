# GitHub Copilot 利用ガイド

Nabledge-6を GitHub Copilot で使用するためのガイドです。

## 前提条件

- **WSL または GitBash 環境**
  - VS Code のターミナルを使用する場合は、ターミナルを WSL または GitBash に設定してください
  - PowerShell や Command Prompt では動作しません（セットアップスクリプトが `jq` コマンドを使用するため）
- プロジェクトディレクトリで作業していること
- VS Code の GitHub Copilot 拡張機能がインストール済みであること

## インストール

### 1. スキルをプロジェクトに追加

プロジェクトルートで以下のコマンドを実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

実行後、`.claude` ディレクトリがプロジェクトに作成されます。このディレクトリ内のスキル定義を GitHub Copilot が自動的に認識します。

### 2. VS Code でスキルを有効化

VS Code の設定でスキル機能を有効にする必要があります：

1. VS Code の設定を開く（`Cmd/Ctrl + ,`）
2. 「GitHub Copilot」を検索
3. 「Skills」または「スキル」関連の設定を探して有効化

**注**: 設定項目名は GitHub Copilot のバージョンによって異なる場合があります。詳細は GitHub Copilot の公式ドキュメントを参照してください。

### 3. チーム共有

`.claude` ディレクトリをGitにコミット・プッシュしてください。チームメンバーも同じスキルを利用できるようになります。

## 使い方

### 基本的な使い方

GitHub Copilot でスキルを使用するには、**スキル名とメッセージを組み合わせて**指定します：

```
/nabledge-6 Nablarchのバッチ処理の実装方法を教えて
```

```
/nabledge-6 このプロジェクトのコードをNablarchの観点から分析して
```

```
/nabledge-6 UniversalDaoの使い方を教えて
```

**重要**: メッセージだけではスキルが使用されません。必ず `/nabledge-6` を先頭に付けてください。

### コード分析

コード分析ワークフローを実行する場合：

```
/nabledge-6 code-analysis
```

## バージョンアップ

セットアップスクリプトを再実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

更新後、`.claude` ディレクトリの変更をGitにコミット・プッシュしてください。
