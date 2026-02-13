# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.9] - 2026-02-13

### Changed
- セットアップスクリプトをリポジトリルートに配置（UX改善）
- setup-6-cc.sh, setup-6-ghc.sh にリネーム（より明確な命名）
- インストールコマンドのパスを短縮

## [0.8] - 2026-02-13

### Changed
- セットアップスクリプトを分離：setup-cc.sh（Claude Code用）とsetup-ghc.sh（GitHub Copilot用）
- setup-cc.shがsettings.jsonを自動編集（extraKnownMarketplaces + enabledPlugins）
- 既存設定との安全なマージをサポート

## [0.7] - 2026-02-13

### Fixed
- READMEのsetup.sh URLをskills/nabledge-6/配下のパスに修正

## [0.6] - 2026-02-13

### Fixed
- スキルディレクトリ構成を修正：配布時と利用時で同じ構造に統一
- workflows/等をskills/nabledge-6/の中に配置

## [0.5] - 2026-02-13

### Fixed
- setup.shのブランチ指定をdummy-toに変更（テスト用）

## [0.4] - 2026-02-13

### Fixed
- setup.shを修正：配布リポジトリ構造から利用者向けskill構造に正しく展開
- skills/nabledge-6/の内容を.claude/skills/nabledge-6/直下に配置
- 不要な.claude-plugin/をコピーしないように修正

## [0.3] - 2026-02-13

### Fixed
- READMEのsetup.sh URLを配布リポジトリのパスに修正（.claude/skills/ → plugins/）

## [0.2] - 2026-02-13

### Fixed
- setup.shのバグ修正：配布リポジトリの構造に合わせてコピー処理を修正
- Gitリポジトリ外でも実行可能に改善

## [0.1] - 2026-02-13

### Added
- Nablarch 6u3の知識検索機能
- コード分析機能（構造化テンプレート）
- バッチ処理の基礎知識
- データベースアクセスライブラリ
- テスティングフレームワークの基礎
- セキュリティチェックリスト

[0.9]: https://github.com/nablarch/nabledge/releases/tag/0.9
[0.8]: https://github.com/nablarch/nabledge/releases/tag/0.8
[0.7]: https://github.com/nablarch/nabledge/releases/tag/0.7
[0.6]: https://github.com/nablarch/nabledge/releases/tag/0.6
[0.5]: https://github.com/nablarch/nabledge/releases/tag/0.5
[0.4]: https://github.com/nablarch/nabledge/releases/tag/0.4
[0.3]: https://github.com/nablarch/nabledge/releases/tag/0.3
[0.2]: https://github.com/nablarch/nabledge/releases/tag/0.2
[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
