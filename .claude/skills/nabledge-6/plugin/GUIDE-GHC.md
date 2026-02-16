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

## 使い方

### 基本的な使い方

自然言語でNablarchに関する質問や依頼をするだけで、GitHub Copilotが自動的にnabledge-6スキルを使用します。

**例**:
```
Nablarchのバッチ処理の実装方法を教えて
```

```
このプロジェクトのコードをNablarchの観点から分析して
```

```
UniversalDaoの使い方を教えて
```

### 手動実行（オプション）

明示的にスキルを指定したい場合は、エディタで以下のコマンドを実行できます：

```bash
/nabledge-6
```

対話的にNablarchに関する質問や、コード分析を行うことができます。

コード分析を直接実行する場合:

```bash
/nabledge-6 code-analysis
```

## バージョンアップ

セットアップスクリプトを再実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

更新後、`.claude` ディレクトリの変更をGitにコミット・プッシュしてください。
