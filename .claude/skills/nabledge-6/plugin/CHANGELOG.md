# 変更履歴

nabledge-6プラグインの主な変更内容を記録しています。

フォーマットは [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) に基づいています。

## [Unreleased]

### 追加
- セットアップスクリプトの環境変数サポート（`NABLEDGE_REPO`, `NABLEDGE_BRANCH`）により、テストやカスタムリポジトリの使用が可能に
- 利用ガイドの分離：Claude Code向け `GUIDE-CC.md` と GitHub Copilot向け `GUIDE-GHC.md`
- GitHub Copilotセットアップスクリプトによる `.vscode/settings.json` の自動設定（`chat.useAgentSkills`）により、チーム全体でスキル機能を共有可能に

### 変更
- コード分析ワークフローの説明を修正（ドキュメント生成機能であり、改善提案は行わない）
- ドキュメントを目的別に分離（README.mdは概要、GUIDE-CC.mdとGUIDE-GHC.mdは詳細手順）
- 評価版の目的を明確化：知識の有無による違いの体感、ワークフローの理解、現場からの要望収集
- GitHub Copilot利用ガイドのインストール前提条件と手順を明確化（WSL/GitBash必須、VS Code設定、スキル使用形式）
- PowerShell/Command Promptが動作しない理由を説明（jqコマンド要件）
- GitHub Copilotの使用方法を更新：`/nabledge-6 メッセージ`形式が必要（メッセージのみではスキルが呼び出されない）
- Claude Codeの利用方法を更新：自然言語での対話を主要な使用方法として強調
- 利用ガイドから環境変数カスタマイズを削除（開発者向け情報のため）
- macOS固有の注意事項を削除（WSL/GitBash前提のためスコープ外）
- バージョン管理の説明を簡素化：READMEから複雑なバージョンセクションを削除、ユーザーは常に最新版をインストール
- 利用ガイドにバージョンアップセクションを追加：タグ指定による特定バージョンのインストール例を記載
- マーケットプレイス全体のCHANGELOGを作成：バージョン対応表とプラグインCHANGELOGへのリンク

## [0.1] - 2026-02-13

### 追加
- 評価版として、Nablarch 6のバッチ処理に関する基礎知識とコード分析ワークフローを提供

[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
