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

### 知識検索

```bash
/nabledge-6 "バッチ処理の実装方法を教えて"
```

### コード分析

```bash
/nabledge-6 code-analysis
```

## カバー範囲

### Nablarchバージョン
- Nablarch 6u3

### 対応内容
- バッチ処理の基礎
- データベースアクセス
- テスティングフレームワークの基礎
- セキュリティチェックリスト

注：初回リリースのため、カバー範囲は限定的です。今後のバージョンで機能を追加していきます。

## バージョニング

このプラグインは `minor.patch` 形式のバージョニングを使用します：
- **Minor**（1桁目）: 機能追加時にインクリメント（例: 0.1 → 1.0 → 2.0）
- **Patch**（2桁目）: バグ修正と小変更時にインクリメント（例: 0.1 → 0.2, 1.0 → 1.1）

プラグイン名 `nabledge-6` がすでにメジャーバージョン（Nablarch 6）を示しているため、プラグインバージョンは2桁の簡略形式を使用します。

## ライセンス

Apache-2.0

## リンク

- 配布リポジトリ: https://github.com/nablarch/nabledge
- 開発リポジトリ: https://github.com/nablarch/nabledge-dev
