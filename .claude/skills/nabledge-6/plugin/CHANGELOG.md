# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.5] - 2026-02-13

### Changed
- Claude Codeのインストール手順をコマンドベースに修正
- settings.jsonは手動作成ではなく、コマンド実行で自動更新される流れを明記
- バージョン指定もコマンドで実行（マーケットプレイス再追加）

## [0.4] - 2026-02-13

### Changed
- READMEをチーム設定前提に簡素化
- マーケットプレイスREADMEをシンプルな構成に戻す
- インストール手順を「settings.jsonをGitにプッシュ」「.claudeディレクトリをGitにプッシュ」に明確化

## [0.3] - 2026-02-13

### Added
- チーム設定方法をREADMEに追加（プロジェクトスコープインストール）
- バージョンアップ方法を追加（Claude Code、GitHub Copilot）
- 自動タグ作成機能をGitHub Actionに追加

### Changed
- インストールコマンドに`--scope project`オプションを追加
- マーケットプレイスREADMEにバージョン管理情報を追加

## [0.2] - 2026-02-13

### Changed
- 機能セクションを「知識」と「ワークフロー」に分類
- マーケットプレイスREADMEにNabledgeの目的と必要性を明記
- プラグイン一覧を状態列付きテーブル形式に変更

## [0.1] - 2026-02-13

### Added
- Nablarch 6u3の知識検索機能
- コード分析機能（構造化テンプレート）
- バッチ処理の基礎知識
- データベースアクセスライブラリ
- テスティングフレームワークの基礎
- セキュリティチェックリスト

[0.1]: https://github.com/nablarch/nabledge/releases/tag/v0.1
