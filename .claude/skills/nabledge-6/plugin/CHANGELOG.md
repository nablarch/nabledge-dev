# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Environment variable support for setup scripts (`NABLEDGE_REPO`, `NABLEDGE_BRANCH`) to enable testing and custom repository usage
- Separate usage guides: `GUIDE-CC.md` for Claude Code and `GUIDE-GHC.md` for GitHub Copilot

### Changed
- Corrected code analysis workflow description (generates documentation, does not provide improvement suggestions)
- Split documentation into focused guides (README.md for overview, GUIDE-CC.md and GUIDE-GHC.md for detailed instructions)
- Enhanced evaluation notice to clarify purpose: experience knowledge impact, understand workflow possibilities, and gather requirements
- Clarified installation prerequisites and procedures in GitHub Copilot guide (WSL/GitBash required, VS Code settings, skill usage format)
- Explained why PowerShell/Command Prompt doesn't work (jq command requirement)
- Updated GitHub Copilot usage to require `/nabledge-6 message` format (message-only doesn't invoke skill)
- Updated usage instructions to emphasize natural language interaction as primary method for Claude Code
- Removed environment variable customization from user guides (developer-only information)
- Removed macOS-specific notes (out of scope for WSL/GitBash prerequisites)

## [0.1] - 2026-02-13

### Added
- Nablarch 6u3の知識検索機能
- コード分析機能（構造化テンプレート）
- バッチ処理の基礎知識
- データベースアクセスライブラリ
- テスティングフレームワークの基礎
- セキュリティチェックリスト

[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
