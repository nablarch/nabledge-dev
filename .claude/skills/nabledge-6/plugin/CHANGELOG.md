# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Environment variable support for setup scripts (`NABLEDGE_REPO`, `NABLEDGE_BRANCH`) to enable testing and custom repository usage
- Separate usage guides: `USAGE-CC.md` for Claude Code and `USAGE-GHC.md` for GitHub Copilot

### Changed
- Split documentation into focused guides (README.md for overview, USAGE-CC.md and USAGE-GHC.md for detailed instructions)
- Clarified installation prerequisites in usage guides (Claude Code requires CC installed, GitHub Copilot requires WSL or GitBash)
- Fixed environment variable usage examples in usage guides (download script first, then execute with env vars)

## [0.1] - 2026-02-13

### Added
- Nablarch 6u3の知識検索機能
- コード分析機能（構造化テンプレート）
- バッチ処理の基礎知識
- データベースアクセスライブラリ
- テスティングフレームワークの基礎
- セキュリティチェックリスト

[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
