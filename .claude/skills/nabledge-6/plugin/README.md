# Nabledge-6 プラグイン

Nablarch 6のAI支援開発スキルです。

## 機能

- **知識検索**: Nablarch 6のドキュメントとベストプラクティスを検索
- **コード分析**: Nablarchの観点からアプリケーションコードを分析

## インストール

### Claude Code

```bash
# マーケットプレイスを追加
/plugin marketplace add nablarch/nabledge

# プラグインをインストール
/plugin install nabledge-6@nabledge
```

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

## 対応範囲（Nablarch 6u3）

### できること
- バッチ処理の基礎知識の検索
- データベースアクセスの実装方法の検索
- テスティングフレームワークの使い方の検索
- セキュリティチェックリストの確認
- プロジェクトコードのNablarch観点での分析

### 今後対応予定
- RESTful Webサービスの知識
- ハンドラの詳細仕様
- より詳細なコード分析機能

注：評価版のため、対応範囲は限定的です。フィードバックをもとに機能を拡充していきます。
