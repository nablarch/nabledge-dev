# Excel Sheet Mapping — Conversion Policy

**Total sheets**: 212 (across all versions)

## Pattern Definitions

| Pattern | Count | Description |
|---------|-------|-------------|
| P1 | 95 | Header detected → structured sections (existing behavior, no change) |
| P2-1 | 16 | Column-indent → Markdown headings (col0=H1, col1=H2, col2=H3, col3+=body) |
| P2-2 | 96 | Current behavior maintained (step tables, single-col lists, etc.) |
| P2-3 | 5 | Embedded LF preserved as Markdown line breaks (`  \n`) |

## Sheet List

### v6

| File | Sheet | Pattern | Notes |
|------|-------|---------|-------|
| Nablarch機能のセキュリティ対応表.xlsx | 改訂履歴 | P1 |  |
| Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | P2-1 | column-indent structure |
| Nablarch機能のセキュリティ対応表.xlsx | 2.チェックリスト | P1 |  |
| Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | P2-3 | embedded LF cells |
| nablarch6-releasenote.xlsx | 6 | P1 |  |
| nablarch6-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch6-releasenote.xlsx | モジュールバージョン一覧 | P1 |  |
| nablarch6u1-releasenote.xlsx | 6u1 | P1 |  |
| nablarch6u1-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch6u1-releasenote.xlsx | 件数取得SQLの拡張ポイント追加 | P2-2 |  |
| nablarch6u2-releasenote.xlsx | 6u2（5u25からの変更点） | P1 |  |
| nablarch6u2-releasenote.xlsx | 6u2 (6u1からの変更点) | P1 |  |
| nablarch6u2-releasenote.xlsx | バージョンアップ手順 | P2-3 | embedded LF cells |
| nablarch6u2-releasenote.xlsx | モジュールバージョン一覧 | P1 |  |
| nablarch6u3-releasenote.xlsx | 6u3 | P1 |  |
| nablarch6u3-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch6u3-releasenote.xlsx | マルチパートリクエストのサポート対応 | P2-1 | column-indent structure |

### v5

| File | Sheet | Pattern | Notes |
|------|-------|---------|-------|
| Nablarch機能のセキュリティ対応表.xlsx | 改訂履歴 | P1 |  |
| Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | P2-1 | column-indent structure |
| Nablarch機能のセキュリティ対応表.xlsx | 2.チェックリスト | P1 |  |
| Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | P2-3 | embedded LF cells |
| nablarch5-releasenote.xlsx | 5 | P1 |  |
| nablarch5-releasenote.xlsx | 別紙_データベースアクセス機能の変更内容 | P1 |  |
| nablarch5-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch5-releasenote.xlsx | 別紙_分割後jarの取り込み | P2-1 | column-indent structure |
| nablarch5-releasenote.xlsx | 別紙_標準プラグインの変更履歴 | P1 |  |
| nablarch5u1-releasenote.xlsx | 5u1 | P1 |  |
| nablarch5u1-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch5u1-releasenote.xlsx | 別紙_テスト用APIの移動内容 | P1 |  |
| nablarch5u1-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u10-releasenote.xlsx | 5u10 | P1 |  |
| nablarch5u10-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u10-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u11-releasenote.xlsx | 5u11 | P1 |  |
| nablarch5u11-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u12-releasenote.xlsx | 5u12 | P1 |  |
| nablarch5u12-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u12-releasenote.xlsx | NumberRangeの対応方法 | P2-2 |  |
| nablarch5u12-releasenote.xlsx | データベースアクセスの型変換機能削除の対応方法 | P2-1 | column-indent structure |
| nablarch5u13-releasenote.xlsx | 5u13 | P1 |  |
| nablarch5u13-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u13-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u13-releasenote.xlsx | Domaのロガーを5u12までと同じ動作にする方法 | P2-2 |  |
| nablarch5u13-releasenote.xlsx | 定型メール送信要求を5u12までと同じ動作にする方法 | P2-2 |  |
| nablarch5u13-releasenote.xlsx | システムリポジトリを5u12までと同じ動作にする方法 | P2-2 |  |
| nablarch5u14-releasenote.xlsx | 5u14 | P1 |  |
| nablarch5u14-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u14-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u14-releasenote.xlsx | ボタンのアイコンを変更する場合 | P2-2 |  |
| nablarch5u14-releasenote.xlsx | HIDDENストア脆弱性 | P2-1 | column-indent structure |
| nablarch5u14-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | P2-1 | column-indent structure |
| nablarch5u15-releasenote.xlsx | 5u15 | P1 |  |
| nablarch5u15-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u15-releasenote.xlsx | 標準プラグインの変更点 | P2-2 |  |
| nablarch5u15-releasenote.xlsx | テスティングフレームワークの設定変更方法 | P2-1 | column-indent structure |
| nablarch5u15-releasenote.xlsx | HttpServerクラスを使っている場合の対応方法 | P2-2 |  |
| nablarch5u16-releasenote.xlsx | 5u16 | P1 |  |
| nablarch5u16-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u16-releasenote.xlsx | Jackson1系の使用有無判断方法 | P2-2 |  |
| nablarch5u16-releasenote.xlsx | Jackson1系の設定変更方法 | P2-2 |  |
| nablarch5u17-releasenote.xlsx | 5u17 | P1 |  |
| nablarch5u17-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u18-releasenote.xlsx | 5u18 | P1 |  |
| nablarch5u18-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u18-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u19-releasenote.xlsx | 5u19 | P1 |  |
| nablarch5u19-releasenote.xlsx | JSON読み取り失敗ケース | P2-1 | column-indent structure |
| nablarch5u19-releasenote.xlsx | Content-Typeの互換性維持方法 | P2-1 | column-indent structure |
| nablarch5u19-releasenote.xlsx | 環境依存値の設定方法 | P2-1 | column-indent structure |
| nablarch5u19-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u19-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u2-releasenote.xlsx | 5u2 | P1 |  |
| nablarch5u2-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch5u2-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u20-releasenote.xlsx | 5u20 | P1 |  |
| nablarch5u20-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u21-releasenote.xlsx | 5u21 | P1 |  |
| nablarch5u21-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u21-releasenote.xlsx | 使用不許可APIチェックツールの設定方法 | P2-2 |  |
| nablarch5u22-releasenote.xlsx | 5u22 | P1 |  |
| nablarch5u22-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u23-releasenote.xlsx | 5u23 | P1 |  |
| nablarch5u23-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u23-releasenote.xlsx | DBアクセス失敗時の例外ハンドリング | P2-2 |  |
| nablarch5u24-releasenote.xlsx | 5u24 | P1 |  |
| nablarch5u24-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u24-releasenote.xlsx | 件数取得SQLの拡張ポイント追加 | P2-2 |  |
| nablarch5u25-releasenote.xlsx | 5u25 | P1 |  |
| nablarch5u25-releasenote.xlsx | バージョンアップ手順 | P2-3 | embedded LF cells |
| nablarch5u26-releasenote.xlsx | 5u26 | P1 |  |
| nablarch5u26-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u26-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u3-releasenote.xlsx | 5u3 | P1 |  |
| nablarch5u3-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch5u3-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u4-releasenote.xlsx | 5u4 | P1 |  |
| nablarch5u4-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch5u4-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u5-releasenote.xlsx | 5u5 | P1 |  |
| nablarch5u5-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u5-releasenote.xlsx | データベース機能のバージョンアップ対応 | P2-1 | column-indent structure |
| nablarch5u5-releasenote.xlsx | ブランクプロジェクト・ドキュメントの刷新について | P1 |  |
| nablarch5u5-releasenote.xlsx | 非推奨ツールについて | P1 |  |
| nablarch5u5-releasenote.xlsx | 認可データ設定ツールのバージョンアップ方法 | P2-3 | embedded LF cells |
| nablarch5u6-releasenote.xlsx | 5u6 | P1 |  |
| nablarch5u6-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u6-releasenote.xlsx | X-Frame-Optoinsの設定 | P2-2 |  |
| nablarch5u6-releasenote.xlsx | メッセージ分割 | P2-1 | column-indent structure |
| nablarch5u6-releasenote.xlsx | 標準プラグインの変更点 | P1 |  |
| nablarch5u7-releasenote.xlsx | 5u7 | P1 |  |
| nablarch5u7-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u8-releasenote.xlsx | 5u8 | P1 |  |
| nablarch5u8-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u9-releasenote.xlsx | 5u9 | P1 |  |
| nablarch5u9-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch5u9-releasenote.xlsx | ETLの設定変更内容 | P2-2 |  |
| nablarch5u9-releasenote.xlsx | メール送信の設定変更内容 | P2-1 | column-indent structure |

### v1.4

| File | Sheet | Pattern | Notes |
|------|-------|---------|-------|
| nablarch-1.4.0-releasenote.xlsx | リリースノート | P1 |  |
| nablarch-1.4.0-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.0.4-releasenote.xlsx | リリースノート | P1 |  |
| nablarch-1.4.0.4-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.1-releasenote.xlsx | 1.4.1 | P1 |  |
| nablarch-1.4.1-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.1.1-releasenote.xlsx | 1.4.1 | P1 |  |
| nablarch-1.4.1.1-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.10-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.10-releasenote.xlsx | 1.4.10 | P1 |  |
| nablarch-1.4.10-releasenote.xlsx | JSON読み取り失敗ケース | P2-1 | column-indent structure |
| nablarch-1.4.10-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.11-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.11-releasenote.xlsx | 1.4.11 | P1 |  |
| nablarch-1.4.11-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.2-releasenote.xlsx | 1.4.2 | P1 |  |
| nablarch-1.4.2-releasenote.xlsx | 別紙_標準プラグインの変更履歴 | P1 |  |
| nablarch-1.4.2-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.3-releasenote.xlsx | 1.4.3 | P1 |  |
| nablarch-1.4.3-releasenote.xlsx | 別紙_標準プラグインの変更履歴 | P1 |  |
| nablarch-1.4.3-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.4-releasenote.xlsx | 1.4.4 | P1 |  |
| nablarch-1.4.4-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.5-releasenote.xlsx | 1.4.5 | P1 |  |
| nablarch-1.4.5-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.6-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.6-releasenote.xlsx | 1.4.6 | P1 |  |
| nablarch-1.4.6-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.7-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.7-releasenote.xlsx | 1.4.7 | P1 |  |
| nablarch-1.4.7-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.8-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.8-releasenote.xlsx | 1.4.8 | P1 |  |
| nablarch-1.4.8-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.8-releasenote.xlsx | リポジトリを1.4.7までと同じ動作にする方法 | P2-2 |  |
| nablarch-1.4.8-releasenote.xlsx | NumberRangeの対応方法 | P2-2 |  |
| nablarch-1.4.9-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.4.9-releasenote.xlsx | 1.4.9 | P1 |  |
| nablarch-1.4.9-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.4.9-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | P2-1 | column-indent structure |

### v1.3

| File | Sheet | Pattern | Notes |
|------|-------|---------|-------|
| nablarch-1.3.2-releasenote.xlsx | 1.3.2 | P1 |  |
| nablarch-1.3.2-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.3.3-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.3.3-releasenote.xlsx | 1.3.3 | P1 |  |
| nablarch-1.3.3-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.3.4-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.3.4-releasenote.xlsx | 1.3.4 | P1 |  |
| nablarch-1.3.4-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.3.5-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.3.5-releasenote.xlsx | 1.3.5 | P1 |  |
| nablarch-1.3.5-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.3.5-releasenote.xlsx | リポジトリを1.3.4までと同じ動作にする方法 | P2-2 |  |
| nablarch-1.3.5-releasenote.xlsx | NumberRangeの対応方法 | P2-2 |  |
| nablarch-1.3.6-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.3.6-releasenote.xlsx | 1.3.6 | P1 |  |
| nablarch-1.3.6-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.3.7-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.3.7-releasenote.xlsx | 1.3.7 | P1 |  |
| nablarch-1.3.7-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch_toolbox-1.3.0-releasenote-detail.xls | リリースノート_Nablarch Toolbox | P1 |  |
| nablarch_toolbox-1.3.1-releasenote-detail.xls | リリースノート_Nablarch Toolbox | P1 |  |
| nablarch_ガイド-1.3.0-releasenote-detail.xls | リリースノート_Nablarchガイド | P1 |  |
| nablarch_ガイド-1.3.1-releasenote-detail.xls | リリースノート_Nablarchガイド | P1 |  |
| nablarch_サンプル-1.3.0-releasenote-detail.xls | リリースノート_Nablarchサンプル | P1 |  |
| nablarch_ライブラリ-1.3.0-releasenote-detail.xls | リリースノート_Nablarchライブラリ | P1 |  |
| nablarch_ライブラリ-1.3.1-releasenote-detail.xls | リリースノート_Nablarchライブラリ | P1 |  |
| nablarch_標準-1.3.0-releasenote-detail.xls | リリースノート_Nablarch標準 | P1 |  |

### v1.2

| File | Sheet | Pattern | Notes |
|------|-------|---------|-------|
| nablarch-1.2.3-releasenote.xlsx | 1.2.3 | P1 |  |
| nablarch-1.2.3-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.2.4-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.2.4-releasenote.xlsx | 1.2.4 | P1 |  |
| nablarch-1.2.4-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.2.5-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.2.5-releasenote.xlsx | 1.2.5 | P1 |  |
| nablarch-1.2.5-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.2.6-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.2.6-releasenote.xlsx | 1.2.6 | P1 |  |
| nablarch-1.2.6-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.2.6-releasenote.xlsx | リポジトリを1.2.5までと同じ動作にする方法 | P2-2 |  |
| nablarch-1.2.6-releasenote.xlsx | NumberRangeの対応方法 | P2-2 |  |
| nablarch-1.2.7-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.2.7-releasenote.xlsx | 1.2.7 | P1 |  |
| nablarch-1.2.7-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch-1.2.8-releasenote.xlsx | 分類 | P2-2 | single-col classification list |
| nablarch-1.2.8-releasenote.xlsx | 1.2.8 | P1 |  |
| nablarch-1.2.8-releasenote.xlsx | バージョンアップ手順 | P2-2 | step table (No/適用手順) |
| nablarch_toolbox-1.2.0-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ガイド-1.2.0-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ガイド-1.2.1-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ガイド-1.2.2-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_サンプル-1.2.0-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ライブラリ-1.2.0-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ライブラリ-1.2.1-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_ライブラリ-1.2.2-releasenote-detail.xls | リリースノート | P1 |  |
| nablarch_開発標準-1.2.0-releasenote-detail.xls | リリースノート | P1 |  |
