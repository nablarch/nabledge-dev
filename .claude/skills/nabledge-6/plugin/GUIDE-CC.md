# Claude Code 利用ガイド

Nabledge-6を Claude Code で使用するためのガイドです。

## 前提条件

- Claude Code がインストール済みであること
- プロジェクトディレクトリで作業していること

## インストール

プロジェクトルートで以下のコマンドを実行：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-cc.sh | bash
```

実行後、`.claude/skills/nabledge-6/` ディレクトリが作成され、スキルファイルがコピーされます。Claude Code は自動的にスキルを認識し、再起動は不要です。

### チーム共有

`.claude/skills/` ディレクトリをGitにコミット・プッシュしてください。チームメンバーがリポジトリをクローンすると、自動的にnabledge-6スキルが利用可能になります。

## 使い方

### 基本的な使い方

自然言語でNablarchに関する質問や依頼をするだけで、Claude Codeが自動的にnabledge-6スキルを使用します。

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

明示的にスキルを指定したい場合は、以下のコマンドで手動実行できます：

```bash
/nabledge-6
```

対話的にNablarchに関する質問や、コード分析を行うことができます。

コード分析を直接実行する場合:

```bash
/nabledge-6 code-analysis
```

## トラブルシューティング

### スキルが認識されない

**確認事項**:
1. `.claude/skills/nabledge-6/SKILL.md` ファイルが存在するか確認
   ```bash
   ls -la .claude/skills/nabledge-6/SKILL.md
   ```

2. Claude Codeを再起動
   ```bash
   # Claude Codeを完全に終了してから再起動
   ```

3. セットアップスクリプトを再実行
   ```bash
   curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-cc.sh | bash
   ```

### エラーメッセージが表示される

**"command not found"**:
- Claude Codeが正しくインストールされているか確認
- PATHが正しく設定されているか確認

**"Permission denied"**:
- `.claude/` ディレクトリの書き込み権限を確認
- `chmod -R u+w .claude/` で権限を付与

**"jq: command not found"**:
- jqがインストールされているか確認: `jq --version`
- 未インストールの場合、セットアップスクリプトを再実行

### セットアップスクリプトが失敗する

**"plugins/nabledge-6 directory not found"**:
- リポジトリ構造が変更された可能性があります
- Issue報告: https://github.com/nablarch/nabledge/issues

**"Installation verification failed"**:
- ネットワーク接続を確認
- 一時ディレクトリ (`/tmp`) に十分な空き容量があるか確認
- セットアップスクリプトを再実行

## バージョンアップ

### 最新版へのアップデート（推奨）

セットアップスクリプトを再実行すると、常に最新版がインストールされます：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-cc.sh | bash
```

実行後、更新された `.claude/skills/` ディレクトリをGitにコミット・プッシュしてください。

### 特定バージョンの指定（オプション）

特定のバージョンにしたい場合は、タグを指定できます：

```bash
# バージョン 0.2 にする場合
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/setup-6-cc.sh -o setup.sh
NABLEDGE_BRANCH=0.2 bash setup.sh
```

実行後、`.claude/skills/` ディレクトリをGitにコミット・プッシュしてください。

**注**: 通常は最新版の使用を推奨します。特定バージョンの指定は、動作検証やトラブルシューティングが必要な場合のみ使用してください。
