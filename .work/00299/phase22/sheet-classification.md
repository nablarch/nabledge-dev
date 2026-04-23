# Excel シート分類結果 (Phase 22-B-9)

converter と verify は §8-2 header 検出規則を独立実装している。
このファイルは **verify 側** の判定結果を出力する (converter と同じ
アルゴリズムから独立に導出されたもの)。

- **P1 (表)**: ヘッダ行 (連続非空セル ≥ 3) + データ行 ≥ 2 + 列数 > 2
- **P2 (段落)**: 上記いずれか不成立


## Version 6

| ファイル | シート | 判定 | 理由 | rows | cols | data rows |
| --- | --- | --- | --- | --- | --- | --- |
| `nablarch6-releasenote.xlsx` | `6` | **P1** | header row=4, data_start=6, cols=122 | 29 | 122 | 17 |
| `nablarch6-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=0 ≤ 2 | 4 | 6 | — |
| `nablarch6-releasenote.xlsx` | `モジュールバージョン一覧` | **P1** | header row=5, data_start=6, cols=5 | 80 | 5 | 75 |
| `nablarch6u1-releasenote.xlsx` | `6u1` | **P1** | header row=4, data_start=6, cols=125 | 29 | 125 | 23 |
| `nablarch6u1-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch6u1-releasenote.xlsx` | `件数取得SQLの拡張ポイント追加` | **P2** | useful_width=0 ≤ 2 | 30 | 2 | — |
| `nablarch6u2-releasenote.xlsx` | `6u2（5u25からの変更点）` | **P1** | header row=4, data_start=6, cols=84 | 64 | 84 | 53 |
| `nablarch6u2-releasenote.xlsx` | `6u2 (6u1からの変更点)` | **P1** | header row=4, data_start=6, cols=82 | 54 | 82 | 42 |
| `nablarch6u2-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 14 | 6 | — |
| `nablarch6u2-releasenote.xlsx` | `モジュールバージョン一覧` | **P1** | header row=5, data_start=6, cols=5 | 81 | 5 | 76 |
| `nablarch6u3-releasenote.xlsx` | `6u3` | **P1** | header row=4, data_start=6, cols=124 | 45 | 124 | 33 |
| `nablarch6u3-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch6u3-releasenote.xlsx` | `マルチパートリクエストのサポート対応` | **P2** | useful_width=0 ≤ 2 | 58 | 6 | — |
| `Nablarch機能のセキュリティ対応表.xlsx` | `改訂履歴` | **P1** | header row=3, data_start=5, cols=9 | 11 | 9 | 6 |
| `Nablarch機能のセキュリティ対応表.xlsx` | `1.概要` | **P2** | useful_width=2 ≤ 2 | 48 | 10 | — |
| `Nablarch機能のセキュリティ対応表.xlsx` | `2.チェックリスト` | **P1** | header row=7, data_start=9, cols=12 | 59 | 12 | 50 |
| `Nablarch機能のセキュリティ対応表.xlsx` | `3.PCIDSS対応表` | **P2** | useful_width=2 ≤ 2 | 16 | 3 | — |

計: P1 = 9, P2 = 8

## Version 5

| ファイル | シート | 判定 | 理由 | rows | cols | data rows |
| --- | --- | --- | --- | --- | --- | --- |
| `nablarch5-releasenote.xlsx` | `5` | **P1** | header row=4, data_start=6, cols=131 | 131 | 131 | 126 |
| `nablarch5-releasenote.xlsx` | `別紙_データベースアクセス機能の変更内容` | **P1** | header row=4, data_start=5, cols=7 | 10 | 7 | 6 |
| `nablarch5-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch5-releasenote.xlsx` | `別紙_分割後jarの取り込み` | **P2** | no header detected (max run_length=1) | 51 | 22 | — |
| `nablarch5-releasenote.xlsx` | `別紙_標準プラグインの変更履歴` | **P1** | header row=7, data_start=8, cols=14 | 59 | 14 | 52 |
| `nablarch5u1-releasenote.xlsx` | `5u1` | **P1** | header row=4, data_start=5, cols=131 | 17 | 131 | 12 |
| `nablarch5u1-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch5u1-releasenote.xlsx` | `別紙_テスト用APIの移動内容` | **P1** | header row=5, data_start=6, cols=7 | 7 | 7 | 2 |
| `nablarch5u1-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u2-releasenote.xlsx` | `5u2` | **P1** | header row=4, data_start=5, cols=131 | 16 | 131 | 11 |
| `nablarch5u2-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch5u2-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u3-releasenote.xlsx` | `5u3` | **P1** | header row=4, data_start=5, cols=131 | 15 | 131 | 10 |
| `nablarch5u3-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch5u3-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u4-releasenote.xlsx` | `5u4` | **P1** | header row=4, data_start=5, cols=131 | 10 | 131 | 5 |
| `nablarch5u4-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch5u4-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u5-releasenote.xlsx` | `5u5` | **P1** | header row=4, data_start=5, cols=128 | 69 | 128 | 64 |
| `nablarch5u5-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u5-releasenote.xlsx` | `データベース機能のバージョンアップ対応` | **P2** | useful_width=0 ≤ 2 | 46 | 54 | — |
| `nablarch5u5-releasenote.xlsx` | `ブランクプロジェクト・ドキュメントの刷新について` | **P1** | header row=4, data_start=5, cols=4 | 19 | 4 | 15 |
| `nablarch5u5-releasenote.xlsx` | `非推奨ツールについて` | **P1** | header row=4, data_start=5, cols=8 | 11 | 8 | 5 |
| `nablarch5u5-releasenote.xlsx` | `認可データ設定ツールのバージョンアップ方法` | **P2** | useful_width=2 ≤ 2 | 20 | 2 | — |
| `nablarch5u10-releasenote.xlsx` | `5u10` | **P1** | header row=4, data_start=5, cols=125 | 74 | 125 | 69 |
| `nablarch5u10-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u10-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=7, data_start=8, cols=7 | 15 | 7 | 8 |
| `nablarch5u11-releasenote.xlsx` | `5u11` | **P1** | header row=4, data_start=5, cols=125 | 49 | 125 | 44 |
| `nablarch5u11-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u12-releasenote.xlsx` | `5u12` | **P1** | header row=4, data_start=6, cols=126 | 41 | 126 | 36 |
| `nablarch5u12-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u12-releasenote.xlsx` | `NumberRangeの対応方法` | **P2** | useful_width=0 ≤ 2 | 18 | 2 | — |
| `nablarch5u12-releasenote.xlsx` | `データベースアクセスの型変換機能削除の対応方法` | **P2** | useful_width=0 ≤ 2 | 45 | 4 | — |
| `nablarch5u13-releasenote.xlsx` | `5u13` | **P1** | header row=4, data_start=6, cols=126 | 87 | 126 | 79 |
| `nablarch5u13-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u13-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=7, data_start=8, cols=7 | 11 | 7 | 4 |
| `nablarch5u13-releasenote.xlsx` | `Domaのロガーを5u12までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 31 | 2 | — |
| `nablarch5u13-releasenote.xlsx` | `定型メール送信要求を5u12までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 29 | 2 | — |
| `nablarch5u13-releasenote.xlsx` | `システムリポジトリを5u12までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 85 | 2 | — |
| `nablarch5u14-releasenote.xlsx` | `5u14` | **P1** | header row=2, data_start=4, cols=16 | 40 | 16 | 30 |
| `nablarch5u14-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u14-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=12, data_start=13, cols=7 | 45 | 7 | 33 |
| `nablarch5u14-releasenote.xlsx` | `ボタンのアイコンを変更する場合` | **P2** | useful_width=0 ≤ 2 | 13 | 3 | — |
| `nablarch5u14-releasenote.xlsx` | `HIDDENストア脆弱性` | **P2** | no header detected (max run_length=1) | 159 | 50 | — |
| `nablarch5u14-releasenote.xlsx` | `汎用データフォーマットXXE脆弱性` | **P2** | useful_width=0 ≤ 2 | 104 | 32 | — |
| `nablarch5u15-releasenote.xlsx` | `5u15` | **P1** | header row=4, data_start=6, cols=126 | 41 | 126 | 30 |
| `nablarch5u15-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u15-releasenote.xlsx` | `標準プラグインの変更点` | **P2** | no header detected (max run_length=6) | 14 | 7 | — |
| `nablarch5u15-releasenote.xlsx` | `テスティングフレームワークの設定変更方法` | **P2** | useful_width=0 ≤ 2 | 54 | 4 | — |
| `nablarch5u15-releasenote.xlsx` | `HttpServerクラスを使っている場合の対応方法` | **P2** | useful_width=0 ≤ 2 | 26 | 14 | — |
| `nablarch5u16-releasenote.xlsx` | `5u16` | **P1** | header row=4, data_start=6, cols=126 | 75 | 126 | 34 |
| `nablarch5u16-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u16-releasenote.xlsx` | `Jackson1系の使用有無判断方法` | **P2** | useful_width=0 ≤ 2 | 12 | 9 | — |
| `nablarch5u16-releasenote.xlsx` | `Jackson1系の設定変更方法` | **P2** | useful_width=0 ≤ 2 | 54 | 13 | — |
| `nablarch5u17-releasenote.xlsx` | `5u17` | **P1** | header row=4, data_start=6, cols=126 | 43 | 126 | 2 |
| `nablarch5u17-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u18-releasenote.xlsx` | `5u18` | **P1** | header row=4, data_start=6, cols=126 | 68 | 126 | 35 |
| `nablarch5u18-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u18-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=10, data_start=11, cols=10 | 107 | 10 | 97 |
| `nablarch5u19-releasenote.xlsx` | `5u19` | **P1** | header row=4, data_start=6, cols=126 | 65 | 126 | 23 |
| `nablarch5u19-releasenote.xlsx` | `JSON読み取り失敗ケース` | **P2** | no header detected (max run_length=1) | 57 | 13 | — |
| `nablarch5u19-releasenote.xlsx` | `Content-Typeの互換性維持方法` | **P2** | useful_width=0 ≤ 2 | 31 | 17 | — |
| `nablarch5u19-releasenote.xlsx` | `環境依存値の設定方法` | **P2** | useful_width=0 ≤ 2 | 11 | 16 | — |
| `nablarch5u19-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 14 | 6 | — |
| `nablarch5u19-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=10, data_start=11, cols=10 | 108 | 10 | 98 |
| `nablarch5u20-releasenote.xlsx` | `5u20` | **P1** | header row=4, data_start=6, cols=125 | 30 | 125 | 18 |
| `nablarch5u20-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u21-releasenote.xlsx` | `5u21` | **P1** | header row=4, data_start=6, cols=116 | 43 | 116 | 31 |
| `nablarch5u21-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u21-releasenote.xlsx` | `使用不許可APIチェックツールの設定方法` | **P2** | no header detected (max run_length=1) | 33 | 8 | — |
| `nablarch5u22-releasenote.xlsx` | `5u22` | **P1** | header row=4, data_start=6, cols=125 | 42 | 125 | 30 |
| `nablarch5u22-releasenote.xlsx` | `バージョンアップ手順` | **P2** | no header detected (max run_length=2) | 12 | 6 | — |
| `nablarch5u23-releasenote.xlsx` | `5u23` | **P1** | header row=4, data_start=6, cols=125 | 42 | 125 | 30 |
| `nablarch5u23-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u23-releasenote.xlsx` | `DBアクセス失敗時の例外ハンドリング` | **P2** | useful_width=0 ≤ 2 | 51 | 2 | — |
| `nablarch5u24-releasenote.xlsx` | `5u24` | **P1** | header row=4, data_start=6, cols=125 | 24 | 125 | 18 |
| `nablarch5u24-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u24-releasenote.xlsx` | `件数取得SQLの拡張ポイント追加` | **P2** | useful_width=0 ≤ 2 | 30 | 2 | — |
| `nablarch5u25-releasenote.xlsx` | `5u25` | **P1** | header row=4, data_start=6, cols=115 | 23 | 115 | 11 |
| `nablarch5u25-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 7 | 6 | — |
| `nablarch5u26-releasenote.xlsx` | `5u26` | **P1** | header row=4, data_start=6, cols=125 | 21 | 125 | 9 |
| `nablarch5u26-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch5u26-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=10, data_start=11, cols=10 | 111 | 10 | 100 |
| `nablarch5u6-releasenote.xlsx` | `5u6` | **P1** | header row=4, data_start=5, cols=125 | 102 | 125 | 97 |
| `nablarch5u6-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u6-releasenote.xlsx` | `X-Frame-Optoinsの設定` | **P2** | useful_width=0 ≤ 2 | 3 | 2 | — |
| `nablarch5u6-releasenote.xlsx` | `メッセージ分割` | **P2** | useful_width=0 ≤ 2 | 70 | 3 | — |
| `nablarch5u6-releasenote.xlsx` | `標準プラグインの変更点` | **P1** | header row=7, data_start=8, cols=7 | 11 | 7 | 4 |
| `nablarch5u7-releasenote.xlsx` | `5u7` | **P1** | header row=4, data_start=5, cols=125 | 20 | 125 | 15 |
| `nablarch5u7-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u8-releasenote.xlsx` | `5u8` | **P1** | header row=4, data_start=5, cols=125 | 35 | 125 | 30 |
| `nablarch5u8-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u9-releasenote.xlsx` | `5u9` | **P1** | header row=4, data_start=5, cols=125 | 79 | 125 | 74 |
| `nablarch5u9-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 10 | 6 | — |
| `nablarch5u9-releasenote.xlsx` | `ETLの設定変更内容` | **P2** | useful_width=0 ≤ 2 | 0 | 0 | — |
| `nablarch5u9-releasenote.xlsx` | `メール送信の設定変更内容` | **P2** | no header detected (max run_length=1) | 43 | 8 | — |
| `Nablarch機能のセキュリティ対応表.xlsx` | `改訂履歴` | **P1** | header row=3, data_start=5, cols=9 | 11 | 9 | 6 |
| `Nablarch機能のセキュリティ対応表.xlsx` | `1.概要` | **P2** | useful_width=2 ≤ 2 | 48 | 10 | — |
| `Nablarch機能のセキュリティ対応表.xlsx` | `2.チェックリスト` | **P1** | header row=7, data_start=9, cols=12 | 59 | 12 | 50 |
| `Nablarch機能のセキュリティ対応表.xlsx` | `3.PCIDSS対応表` | **P2** | useful_width=2 ≤ 2 | 16 | 3 | — |

計: P1 = 41, P2 = 59

## Version 1.4

| ファイル | シート | 判定 | 理由 | rows | cols | data rows |
| --- | --- | --- | --- | --- | --- | --- |
| `nablarch-1.4.0-releasenote.xlsx` | `リリースノート` | **P1** | header row=4, data_start=6, cols=129 | 52 | 129 | 47 |
| `nablarch-1.4.0-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.0.4-releasenote.xlsx` | `リリースノート` | **P1** | header row=4, data_start=6, cols=129 | 55 | 129 | 50 |
| `nablarch-1.4.0.4-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.1-releasenote.xlsx` | `1.4.1` | **P1** | header row=4, data_start=6, cols=129 | 29 | 129 | 24 |
| `nablarch-1.4.1-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.1.1-releasenote.xlsx` | `1.4.1` | **P1** | header row=4, data_start=6, cols=129 | 38 | 129 | 33 |
| `nablarch-1.4.1.1-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.10-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.10-releasenote.xlsx` | `1.4.10` | **P1** | header row=2, data_start=3, cols=15 | 12 | 15 | 6 |
| `nablarch-1.4.10-releasenote.xlsx` | `JSON読み取り失敗ケース` | **P2** | no header detected (max run_length=1) | 57 | 13 | — |
| `nablarch-1.4.10-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.11-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.11-releasenote.xlsx` | `1.4.11` | **P1** | header row=4, data_start=5, cols=110 | 14 | 110 | 7 |
| `nablarch-1.4.11-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.2-releasenote.xlsx` | `1.4.2` | **P1** | header row=4, data_start=6, cols=130 | 41 | 130 | 36 |
| `nablarch-1.4.2-releasenote.xlsx` | `別紙_標準プラグインの変更履歴` | **P1** | header row=7, data_start=8, cols=14 | 35 | 14 | 24 |
| `nablarch-1.4.2-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.3-releasenote.xlsx` | `1.4.3` | **P1** | header row=4, data_start=6, cols=130 | 24 | 130 | 19 |
| `nablarch-1.4.3-releasenote.xlsx` | `別紙_標準プラグインの変更履歴` | **P1** | header row=7, data_start=8, cols=8 | 17 | 8 | 10 |
| `nablarch-1.4.3-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.4-releasenote.xlsx` | `1.4.4` | **P1** | header row=4, data_start=6, cols=131 | 13 | 131 | 8 |
| `nablarch-1.4.4-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.5-releasenote.xlsx` | `1.4.5` | **P1** | header row=4, data_start=5, cols=130 | 12 | 130 | 7 |
| `nablarch-1.4.5-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.6-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.6-releasenote.xlsx` | `1.4.6` | **P1** | header row=4, data_start=5, cols=124 | 8 | 124 | 3 |
| `nablarch-1.4.6-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.7-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.7-releasenote.xlsx` | `1.4.7` | **P1** | header row=4, data_start=5, cols=124 | 38 | 124 | 33 |
| `nablarch-1.4.7-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.8-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.8-releasenote.xlsx` | `1.4.8` | **P1** | header row=4, data_start=5, cols=112 | 33 | 112 | 26 |
| `nablarch-1.4.8-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.8-releasenote.xlsx` | `リポジトリを1.4.7までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 85 | 2 | — |
| `nablarch-1.4.8-releasenote.xlsx` | `NumberRangeの対応方法` | **P2** | useful_width=0 ≤ 2 | 19 | 2 | — |
| `nablarch-1.4.9-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.4.9-releasenote.xlsx` | `1.4.9` | **P1** | header row=2, data_start=3, cols=15 | 11 | 15 | 5 |
| `nablarch-1.4.9-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.4.9-releasenote.xlsx` | `汎用データフォーマットXXE脆弱性` | **P2** | useful_width=0 ≤ 2 | 104 | 32 | — |

計: P1 = 16, P2 = 24

## Version 1.3

| ファイル | シート | 判定 | 理由 | rows | cols | data rows |
| --- | --- | --- | --- | --- | --- | --- |
| `nablarch_toolbox-1.3.0-releasenote-detail.xls` | `リリースノート_Nablarch Toolbox` | **P2** | no header detected (max run_length=10) | 7 | 10 | — |
| `nablarch_ガイド-1.3.0-releasenote-detail.xls` | `リリースノート_Nablarchガイド` | **P1** | header row=5, data_start=7, cols=10 | 18 | 10 | 12 |
| `nablarch_サンプル-1.3.0-releasenote-detail.xls` | `リリースノート_Nablarchサンプル` | **P1** | header row=5, data_start=7, cols=10 | 15 | 10 | 9 |
| `nablarch_ライブラリ-1.3.0-releasenote-detail.xls` | `リリースノート_Nablarchライブラリ` | **P1** | header row=5, data_start=7, cols=10 | 41 | 10 | 35 |
| `nablarch_標準-1.3.0-releasenote-detail.xls` | `リリースノート_Nablarch標準` | **P1** | header row=5, data_start=7, cols=10 | 16 | 10 | 10 |
| `nablarch_toolbox-1.3.1-releasenote-detail.xls` | `リリースノート_Nablarch Toolbox` | **P2** | no header detected (max run_length=10) | 7 | 10 | — |
| `nablarch_ガイド-1.3.1-releasenote-detail.xls` | `リリースノート_Nablarchガイド` | **P1** | header row=5, data_start=7, cols=10 | 11 | 10 | 5 |
| `nablarch_ライブラリ-1.3.1-releasenote-detail.xls` | `リリースノート_Nablarchライブラリ` | **P1** | header row=5, data_start=7, cols=10 | 24 | 10 | 18 |
| `nablarch-1.3.2-releasenote.xlsx` | `1.3.2` | **P1** | header row=5, data_start=6, cols=130 | 19 | 130 | 13 |
| `nablarch-1.3.2-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.3.3-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.3.3-releasenote.xlsx` | `1.3.3` | **P1** | header row=4, data_start=5, cols=124 | 8 | 124 | 3 |
| `nablarch-1.3.3-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.3.4-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.3.4-releasenote.xlsx` | `1.3.4` | **P1** | header row=4, data_start=5, cols=124 | 33 | 124 | 28 |
| `nablarch-1.3.4-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.3.5-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.3.5-releasenote.xlsx` | `1.3.5` | **P1** | header row=4, data_start=5, cols=112 | 30 | 112 | 23 |
| `nablarch-1.3.5-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.3.5-releasenote.xlsx` | `リポジトリを1.3.4までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 85 | 2 | — |
| `nablarch-1.3.5-releasenote.xlsx` | `NumberRangeの対応方法` | **P2** | useful_width=0 ≤ 2 | 19 | 2 | — |
| `nablarch-1.3.6-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.3.6-releasenote.xlsx` | `1.3.6` | **P1** | header row=4, data_start=5, cols=112 | 13 | 112 | 5 |
| `nablarch-1.3.6-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.3.7-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.3.7-releasenote.xlsx` | `1.3.7` | **P1** | header row=4, data_start=5, cols=110 | 13 | 110 | 6 |
| `nablarch-1.3.7-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |

計: P1 = 12, P2 = 15

## Version 1.2

| ファイル | シート | 判定 | 理由 | rows | cols | data rows |
| --- | --- | --- | --- | --- | --- | --- |
| `nablarch_toolbox-1.2.0-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 13 | 10 | 9 |
| `nablarch_ガイド-1.2.0-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 20 | 10 | 16 |
| `nablarch_サンプル-1.2.0-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 9 | 10 | 5 |
| `nablarch_ライブラリ-1.2.0-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 58 | 10 | 54 |
| `nablarch_開発標準-1.2.0-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 16 | 10 | 12 |
| `nablarch_ガイド-1.2.1-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 12 | 10 | 8 |
| `nablarch_ライブラリ-1.2.1-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 30 | 10 | 26 |
| `nablarch_ガイド-1.2.2-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 10 | 10 | 6 |
| `nablarch_ライブラリ-1.2.2-releasenote-detail.xls` | `リリースノート` | **P1** | header row=3, data_start=5, cols=10 | 19 | 10 | 15 |
| `nablarch-1.2.3-releasenote.xlsx` | `1.2.3` | **P1** | header row=5, data_start=6, cols=130 | 24 | 130 | 18 |
| `nablarch-1.2.3-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.2.4-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.2.4-releasenote.xlsx` | `1.2.4` | **P1** | header row=4, data_start=5, cols=124 | 8 | 124 | 3 |
| `nablarch-1.2.4-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.2.5-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.2.5-releasenote.xlsx` | `1.2.5` | **P1** | header row=4, data_start=5, cols=124 | 32 | 124 | 27 |
| `nablarch-1.2.5-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.2.6-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.2.6-releasenote.xlsx` | `1.2.6` | **P1** | header row=4, data_start=5, cols=112 | 29 | 112 | 22 |
| `nablarch-1.2.6-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.2.6-releasenote.xlsx` | `リポジトリを1.2.5までと同じ動作にする方法` | **P2** | useful_width=0 ≤ 2 | 85 | 2 | — |
| `nablarch-1.2.6-releasenote.xlsx` | `NumberRangeの対応方法` | **P2** | useful_width=0 ≤ 2 | 19 | 2 | — |
| `nablarch-1.2.7-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.2.7-releasenote.xlsx` | `1.2.7` | **P1** | header row=4, data_start=5, cols=112 | 13 | 112 | 5 |
| `nablarch-1.2.7-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |
| `nablarch-1.2.8-releasenote.xlsx` | `分類` | **P2** | useful_width=0 ≤ 2 | 71 | 2 | — |
| `nablarch-1.2.8-releasenote.xlsx` | `1.2.8` | **P1** | header row=4, data_start=5, cols=110 | 13 | 110 | 6 |
| `nablarch-1.2.8-releasenote.xlsx` | `バージョンアップ手順` | **P2** | useful_width=2 ≤ 2 | 9 | 6 | — |

計: P1 = 15, P2 = 13

## 全体計

| version | P1 | P2 | 合計 |
| --- | --- | --- | --- |
| 6 | 9 | 8 | 17 |
| 5 | 41 | 59 | 100 |
| 1.4 | 16 | 24 | 40 |
| 1.3 | 12 | 15 | 27 |
| 1.2 | 15 | 13 | 28 |
| **total** | **93** | **119** | **212** |
