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

実行後、以下のファイルが自動的に作成されます：
- `.claude/skills/nabledge-6/` - スキル定義（GitHub Copilot が自動認識）
- `.vscode/settings.json` - VS Code 設定（GitHub Copilot スキル機能を有効化）

### 2. チーム共有

`.claude` ディレクトリと `.vscode/settings.json` をGitにコミット・プッシュしてください。チームメンバーがリポジトリをクローンすると、自動的に以下が有効になります：
- nabledge-6 スキルの利用
- GitHub Copilot スキル機能の有効化

**注**: チームメンバーは VS Code を再起動する必要があります。

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

### 別コンテキスト実行（推奨）

nabledge-6を**別コンテキスト実行**することで、より高速かつクリーンな回答を得られます。

**実行方法** (GitHub Copilot のビルトインコマンドを使用):
```bash
# GitHub Copilot のビルトインコマンド
/agent nabledge-6
```

その後、通常通り質問を入力します:
```
UniversalDaoでページングを実装する方法
```

**メリット**:
- **会話がスッキリ**: 検索の中間結果が表示されず、回答のみが表示されます
- **高速な応答**: コンテキスト消費量が80%以上削減され、レスポンスが向上します
- **集中できる**: ファイル検索やjq実行などの処理が見えないため、結果に集中できます

**仕組み**:
1. `/agent nabledge-6` で別コンテキスト実行のエージェントを起動
2. エージェントが知識検索ワークフローを実行（10〜20回のツール実行）
3. 整形された回答のみがメイン会話に表示される
4. 中間処理（ファイル検索、jq出力など）は別コンテキスト実行で処理され、表示されない

### 手動実行（代替手段）

別コンテキスト実行が利用できない場合は、従来の手動実行も可能です:

```bash
# 対話モードで起動（手動実行）
/nabledge-6
```

対話的にNablarchに関する質問や、コード分析を行うことができます。

コード分析を直接実行する場合:

```bash
# コード分析を直接実行（手動実行）
/nabledge-6 code-analysis
```

**注**: 手動実行では中間処理も表示されるため、コンテキスト消費量が多くなります。可能な限り `/agent nabledge-6` による別コンテキスト実行を推奨します。

### コマンドリファレンス

**注**: これらのコマンドは、別コンテキスト実行（`/agent nabledge-6`）が利用できない場合の代替手段です。可能な限り別コンテキスト実行を使用してください。

| コマンド | 説明 | 入力形式 | 出力場所・内容 |
|---------|------|---------|--------------|
| `/nabledge-6` | 対話モードで起動（手動実行）。知識検索またはコード分析を選択可能 | なし | なし（対話形式で結果を表示） |
| `/nabledge-6 code-analysis` | 既存コードの構造を分析し、ドキュメントを生成（手動実行） | ターゲットコード指定（対話で入力）<br>例: "LoginAction", "proman-batchモジュール" | `.nabledge/YYYYMMDD/code-analysis-<target>.md`<br>依存関係図、コンポーネント一覧、Nablarch利用状況を含む構造化ドキュメント<br>[テンプレート](../assets/code-analysis-template.md) \| [ガイド](../assets/code-analysis-template-guide.md) \| [例](../assets/code-analysis-template-examples.md) |

## バージョンアップ

### 最新版へのアップデート（推奨）

セットアップスクリプトを再実行すると、常に最新版がインストールされます：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh | bash
```

更新後、`.claude` ディレクトリの変更をGitにコミット・プッシュしてください。

### 特定バージョンの指定（オプション）

特定のバージョンにしたい場合は、タグを指定できます：

```bash
# バージョン 0.2 にする場合
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-ghc.sh -o setup.sh
NABLEDGE_BRANCH=0.2 bash setup.sh
```

更新後、`.claude` ディレクトリの変更をGitにコミット・プッシュしてください。

**注**: 通常は最新版の使用を推奨します。特定バージョンの指定は、動作検証やトラブルシューティングが必要な場合のみ使用してください。
