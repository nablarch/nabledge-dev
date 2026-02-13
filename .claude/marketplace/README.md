# Nablarch スキルマーケットプレイス

Claude CodeとGitHub Copilot向けのNablarch AI支援開発スキルです。

## 利用可能なプラグイン

### nabledge-6

Nablarch 6のAI支援開発スキルです。

**機能**:
- 知識検索: Nablarch 6のドキュメントとベストプラクティスを検索
- コード分析: Nablarchの観点からアプリケーションコードを分析

**インストール**:
```bash
# マーケットプレイスを追加
/plugin marketplace add nablarch/nabledge

# nabledge-6 プラグインをインストール
/plugin install nabledge-6@nabledge
```

**使い方**:
```bash
# 基本的な使い方
/nabledge-6

# 知識検索
/nabledge-6 "バッチ処理の実装方法を教えて"

# コード分析
/nabledge-6 code-analysis
```

**対応範囲**: Nablarch 6u3

できること:
- バッチ処理の基礎知識の検索
- データベースアクセスの実装方法の検索
- テスティングフレームワークの使い方の検索
- セキュリティチェックリストの確認
- プロジェクトコードのNablarch観点での分析

今後対応予定:
- RESTful Webサービスの知識
- ハンドラの詳細仕様
- より詳細なコード分析機能

詳細は [plugins/nabledge-6/README.md](plugins/nabledge-6/README.md) を参照してください。

### nabledge-5 (Coming Soon)

Nablarch 5のAI支援開発スキルは今後提供予定です。

## バージョニング

各プラグインは独立したバージョン管理を行っています：
- **nabledge-6**: `minor.patch` 形式を使用（例: 0.1, 1.0, 2.0）
- プラグイン名がすでにNablarchのメジャーバージョンを示しています

## ライセンス

Apache-2.0

## リンク

- 配布リポジトリ: https://github.com/nablarch/nabledge
- 開発リポジトリ: https://github.com/nablarch/nabledge-dev
