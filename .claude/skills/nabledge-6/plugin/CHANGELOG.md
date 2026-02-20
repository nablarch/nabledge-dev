# 変更履歴

nabledge-6プラグインの主な変更内容を記録しています。

フォーマットは [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) に基づいています。

## [Unreleased]

### 変更
- コード分析の出力先ディレクトリを `.nabledge/` に変更しました。Nabledgeが生成したファイルがプロジェクトのファイルから明確に分離されます（従来は `work/YYYYMMDD/` に出力）
- 知識検索ワークフローを単一ステージ方式に改善しました。ファイル選定→セクション選定の2段階から、セクション直接選定の1段階に変更され、検索速度が36-57%向上しました (Issue #53)

## [0.2] - 2026-02-17

### 修正
- Claude Codeのセットアップスクリプトがマーケットプレイス設定ではなく `.claude/skills/` ディレクトリへ直接スキルをインストールするように変更し、初回起動時に再起動なしで即座に認識されるようになりました (Issue #27)

## [0.1] - 2026-02-16

### 追加
- 評価版として、Nablarch 6のバッチ処理に関する基礎知識とコード分析ワークフローを提供

[0.2]: https://github.com/nablarch/nabledge/releases/tag/0.2
[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
