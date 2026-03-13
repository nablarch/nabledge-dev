# nabledge-dev

[Nabledge](https://github.com/nablarch/nabledge) の開発リポジトリ

## ドキュメント

- 📊 [開発状況](docs/development-status.md) - 現在の進捗とロードマップ
- 📐 [設計ドキュメント](docs/nabledge-design.md) - アーキテクチャと設計の詳細
- 🎯 [アクティビティマッピング](docs/activity-mapping.md) - Nabledge とのワークフローおよび役割分担
- 📈 [メトリクス](docs/metrics.md) - 週次開発生産性と Nabledge 導入状況（自動更新）

## 前提条件

- WSL2 / Ubuntu
- CA 証明書（企業プロキシ環境の場合）

## セットアップ

### 1. CA 証明書のインストール（プロキシ環境の場合）

```bash
sudo cp /path/to/your/ca.crt /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates
```

### 2. 環境セットアップ

```bash
./setup.sh
cp .env.example .env
# .env を編集して認証情報を設定する
```

### 3. Nablarch 1.x ドキュメントのセットアップ（v1.4/1.3/1.2 の知識ファイルを生成する場合）

Nablarch 1.x のドキュメントは GitHub で公開されていないため、ローカルにあるドキュメントディレクトリへのシンボリックリンクを手動で設定する必要があります。

リポジトリルートで以下を実行します（`/path/to/` は実際のローカルパスに置き換えてください）：

```bash
mkdir -p .lw/nab-official/v1.4 .lw/nab-official/v1.3 .lw/nab-official/v1.2
ln -s /path/to/1.4_maintain .lw/nab-official/v1.4/1.4_maintain
ln -s /path/to/1.3_maintain .lw/nab-official/v1.3/1.3_maintain
ln -s /path/to/1.2_maintain .lw/nab-official/v1.2/1.2_maintain
```

設定後、knowledge-creator で知識ファイルを生成できます：

```bash
./tools/knowledge-creator/kc.sh gen 1.4
```

## 使い方

```bash
source .env
claude
```

## ブランチ戦略

このリポジトリはシングルブランチの開発ワークフローを採用しています。すべての開発作業はプルリクエスト経由で **main** ブランチにマージされ、変更は [nablarch/nabledge:develop](https://github.com/nablarch/nabledge/tree/develop) に自動同期されます。

### 開発フロー

```mermaid
flowchart LR
    MAIN["nabledge-dev<br/>main"]
    WB["nabledge-dev<br/>ワーキングブランチ"]
    GHA["GitHub Actions<br/>（自動同期）"]
    DEV["nablarch/nabledge<br/>develop"]
    RELEASE["nablarch/nabledge<br/>main（リリース）"]

    MAIN -->|"ブランチ作成"| WB
    WB -->|"PR マージ"| MAIN
    MAIN -->|"push"| GHA
    GHA -->|"自動同期"| DEV
    DEV -->|"main に追い付きマージ"| RELEASE
```

### 開発バージョンのテスト

`nablarch/nabledge:develop` の最新開発バージョンをテストするには、`tools/tests/test-setup.sh` を使います。

このスクリプトは全バージョン × ツールの組み合わせのテスト環境を一括セットアップします。

**セットアップ手順：**

1. テスト用ワークスペースディレクトリを作成してスクリプトを実行：
   ```bash
   mkdir -p /tmp/nabledge-test && cd /tmp/nabledge-test
   bash /path/to/tools/tests/test-setup.sh
   ```

   スクリプトは以下のディレクトリを作成します：
   | ディレクトリ | 内容 |
   |---|---|
   | `v6/test-cc/` | nabledge-6 × Claude Code |
   | `v6/test-ghc/` | nabledge-6 × GitHub Copilot |
   | `v5/test-cc/` | nabledge-5 × Claude Code |
   | `v5/test-ghc/` | nabledge-5 × GitHub Copilot |
   | `all/test-cc/` | 全バージョン × Claude Code |
   | `all/test-ghc/` | 全バージョン × GitHub Copilot |

2. セットアップを確認：
   ```bash
   ls v6/test-cc/nablarch-example-batch/.claude/skills/
   ls v6/test-ghc/nablarch-example-batch/.claude/skills/
   ```

3. 各ディレクトリの `nablarch-example-batch/` で動作確認：
   - Claude Code の場合：`claude` を起動して `/nabledge-6`
   - GitHub Copilot の場合：VS Code でフォルダを開き、GitHub Copilot Chat で `/n6`

### リリース手順

バージョンファイルと CHANGELOG の更新はこのリポジトリ（nabledge-dev）で行います。その後、[nablarch/nabledge](https://github.com/nablarch/nabledge) リポジトリでリリース作業を行います。

> nablarch/nabledge:develop での動作確認手順は「[開発バージョンのテスト](#開発バージョンのテスト)」を参照してください。

**nablarch/nabledge リポジトリでの手順：**

1. **差分確認用 PR を作成** - `main` から `develop` へ PR を作成し、変更内容をレビュー
2. **develop に追い付きマージ** - リリース OK になったら `main` を `develop` に追い付かせるようにマージ（PR はコミットが作られるため PR 経由ではなく直接マージ）

詳細なリリースワークフローは `.claude/rules/release.md` を参照してください。

## 開発

### カスタムスラッシュコマンド

このリポジトリには開発ワークフローを効率化するカスタムスラッシュコマンドが用意されています：

#### /hi - フル開発ワークフロー
イシュー起票から PR レビュー依頼まで一通りのワークフローを実行します：
```
/hi 123        # イシュー #123 の作業を開始
/hi 456        # イシュー/PR #456 の作業を再開
/hi            # インタラクティブ選択
```
ブランチの作成・変更の実装・テストの実行・PR の作成まで自動で行います。

#### /fb - レビューフィードバック対応
PR レビューのフィードバックに対応します：
```
/fb 456        # PR #456 のレビューに対応
/fb            # 現在のブランチから自動検出
```
コメントを取得し、修正を実装してコミット後、レビュアーに返信します。

#### /bb - マージとクリーンアップ
PR の承認・マージとブランチの後片付けを行います：
```
/bb 456        # PR #456 をマージしてブランチを削除
/bb            # 現在のブランチから自動検出
```
PR を承認してマージし、HEAD を main に切り替えてブランチを削除します。

### nabledge スキルのテスト

nabledge スキルの性能を改善した場合、`nabledge-test` スキルでベースラインと比較して改善効果を確認します。

## フィードバック

### 公開済みの nabledge スキルについて
[nablarch/nabledge Issues](https://github.com/nablarch/nabledge/issues) にイシューを登録するか、機能リクエストをお送りください。他のユーザーも検索・参照しやすくなります。

### 未リリースの開発作業について
[nablarch/nabledge-dev Issues](https://github.com/nablarch/nabledge-dev/issues) にイシューを登録するか、変更内容について議論してください。
