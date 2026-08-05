# nabledge-dev

[Nabledge](https://github.com/nablarch/nabledge) スキルの開発リポジトリです。

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
SVN_BASE_URL=<SVN_URL> SVN_USERNAME=<username> SVN_PASSWORD=<password> ./setup.sh
cp .env.example .env
# .env を編集して認証情報を設定する
```

`SVN_BASE_URL` 等には v1.4/v1.3/v1.2 が格納されている SVN リポジトリの URL を指定します。

## 使い方

```bash
source .env
claude
```

## 開発

### リポジトリ構成

このプロジェクトは 2 つのリポジトリで管理されています。

| リポジトリ | 役割 |
|---|---|
| **nabledge-dev**（このリポジトリ） | スキルの開発・改善を行う作業場 |
| **[nabledge](https://github.com/nablarch/nabledge)** | ユーザーへの配布リポジトリ |

nabledge-dev/main へのプッシュをトリガーに、GitHub Actions が nabledge/develop へ変更を自動同期します。

### フロー

```mermaid
flowchart LR
    MAIN["nabledge-dev/main"]
    WB["nabledge-dev<br/>ワーキングブランチ"]
    BM["ベンチマーク<br/>（影響ある場合）"]
    GHA["GitHub Actions<br/>（自動同期）"]
    DEV["nabledge/develop"]

    MAIN -->|"ブランチ作成"| WB
    WB -.->|"任意"| BM
    WB -->|"PR マージ"| MAIN
    MAIN -->|"push"| GHA
    GHA -->|"自動同期"| DEV
```

### 手順

開発作業は Claude への指示で進めます。**手動**と記載した手順のみユーザーが実行します。

#### スキル改善・不具合対応

1. 作業内容を Claude に伝えて**イシューを作成**
2. `/hi <number>` でスキル変更・PR 作成まで実行
3. ベンチマークを Claude に指示して実行（詳細: [E2Eベンチマーク実行手順](tools/benchmark/HOW-TO-RUN.md)）
   - 問題あり → 2 に戻る
   - 問題なし → 次へ
4. PR をレビュー（**手動**）
5. フィードバックがあれば `/fb <number>` で対応
6. `/bb <number>` で PR をマージ

#### Nablarch ソース更新

1. 作業内容を Claude に伝えて**イシューを作成**
2. `./setup.sh` を再実行して Nablarch ソースを更新（**手動**）
3. `/hi <number>` でナレッジファイルの再生成・PR 作成まで実行
4. ベンチマークを Claude に指示して実行（詳細: [E2Eベンチマーク実行手順](tools/benchmark/HOW-TO-RUN.md)）
   - 問題あり → 3 に戻る
   - 問題なし → 次へ
5. PR をレビュー（**手動**）
6. フィードバックがあれば `/fb <number>` で対応
7. `/bb <number>` で PR をマージ

## リリース

### フロー

nabledge/develop に自動同期された変更を、nabledge/main へリリースします。

```mermaid
flowchart LR
    DEV["nabledge/develop"]
    TEST["セットアップ検証"]
    RB["nabledge/release/{version}"]
    RELEASE["nabledge/main"]

    DEV --> TEST
    TEST -->|"ブランチ作成"| RB
    RB -->|"PR マージ"| RELEASE
```

### 手順

**Claude に指示する作業：**

1. **バージョンファイル・CHANGELOG 更新** — nabledge-dev でバージョンを上げて CHANGELOG を整備します（詳細: `.claude/rules/release.md`）。
2. **セットアップ検証** — `test-setup.sh` を実行し、全バージョンのセットアップが PASS / WARN になることを確認します（詳細: [test-setup.sh — セットアップテスト手順](tools/tests/README.md)）。

**ユーザーが手動で行う作業（nabledge）：**

3. nabledge/develop から `release/{version}` ブランチを作成
4. nabledge/release/{version} から nabledge/main へ PR を作成・マージ

## フィードバック

- 公開済みのスキルについて: [nabledge Issues](https://github.com/nablarch/nabledge/issues)
- 開発中の作業について: [nabledge-dev Issues](https://github.com/nablarch/nabledge-dev/issues)
