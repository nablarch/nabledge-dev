# Nabledge

Nabledgeは、NablarchによるAI支援開発スキルです。Claude CodeやGitHub Copilotといったコーディングエージェントに対して、Nablarchの知識とワークフローを提供します。

コーディングエージェントはNablarchのような企業フレームワークの知識を十分に持っていません。Nabledgeを導入することで、エージェントがNablarchのドキュメントやベストプラクティスを参照しながら開発を支援できるようになります。

## プラグイン

| プラグイン | 対応バージョン | 状態 |
|-----------|-------------|------|
| [nabledge-6](plugins/nabledge-6/README.md) | Nablarch 6u3 | 提供中 |
| nabledge-5 | Nablarch 5 | 今後提供予定 |

インストール方法や使い方は各プラグインのREADMEを参照してください。

## チーム設定

プロジェクトメンバー全員がNabledgeプラグインを利用できるよう、プロジェクトスコープで設定できます。

### 設定方法

プロジェクトルートに `.claude/settings.json` を作成し、以下を追加：

```json
{
  "extraKnownMarketplaces": [
    {
      "name": "nabledge",
      "source": "https://github.com/nablarch/nabledge.git"
    }
  ],
  "enabledPlugins": {
    "nabledge-6@nabledge": {
      "enabled": true
    }
  }
}
```

このファイルをGitにコミットすると、チームメンバーがリポジトリをクローンした際に自動的にプラグインのインストールが促されます。

### VS Codeでの設定

VS Codeでは `.vscode/settings.json` に以下を追加：

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Nablarch framework knowledge is available via nabledge-6 skill"
    }
  ]
}
```

### バージョンアップ

#### Claude Code

マーケットプレイスは起動時に自動更新されます。手動で更新する場合：

```bash
# マーケットプレイスを更新
/plugin marketplace update nabledge

# 特定バージョンを指定する場合
/plugin marketplace add nablarch/nabledge#v0.2
```

#### VS Code (GitHub Copilot)

最新版を再インストール：

```bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/main/.claude/skills/nabledge-6/scripts/setup.sh | bash
```

## バージョニング

各プラグインは独立したバージョン管理を行っています。

- nabledge-6: `minor.patch` 形式を使用（例: 0.1, 1.0, 2.0）
- プラグイン名がすでにNablarchのメジャーバージョンを示しています

## ライセンス

Apache-2.0

## リンク

- 配布リポジトリ: https://github.com/nablarch/nabledge
- 開発リポジトリ: https://github.com/nablarch/nabledge-dev
