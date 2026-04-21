# 機能詳細

## アプリケーションの起動方法

* アプリケーションの起動方法

<details>
<summary>keywords</summary>

アプリケーション起動, 起動方法, main-run_application

</details>

## システムリポジトリの初期化

システムリポジトリの初期化は、アプリケーション起動時にシステムリポジトリの設定ファイルのパスを指定することで行う。
詳細は、アプリケーションの起動方法 を参照。

<details>
<summary>keywords</summary>

システムリポジトリ初期化, 設定ファイルパス指定, アプリケーション起動時初期化

</details>

## データベースアクセス

* データベースアクセス

<details>
<summary>keywords</summary>

データベースアクセス, database_management

</details>

## 入力値のチェック

* 入力値のチェック

<details>
<summary>keywords</summary>

入力値チェック, バリデーション, validation

</details>

## 排他制御

排他制御は、以下の2種類の方法を提供しているが、
UniversalDaoを推奨する理由 に記載がある通り、
ユニバーサルDAO の使用を推奨する。

* 排他制御
* ユニバーサルDAO

* universal_dao_jpa_pessimistic_lock

<details>
<summary>keywords</summary>

排他制御, UniversalDao推奨, universal_dao, exclusive_control, 悲観ロック, universal_dao_jpa_pessimistic_lock

</details>

## 実行制御

* プロセス終了コード
* エラー発生時にエラー応答電文を返す
* メッセージングプロセスを異常終了させる (テーブルをキューとして使ったメッセージングと同じ)
* 処理の並列実行(マルチスレッド化)

<details>
<summary>keywords</summary>

プロセス終了コード, エラー応答電文, メッセージングプロセス異常終了, マルチスレッド並列実行, multi_thread_execution_handler

</details>

## MOMメッセージング

* MOMメッセージング
* 標準提供のデータリーダ

* `FwHeaderReader (電文からフレームワーク制御ヘッダの読み込み)`
* `MessageReader (MQから電文の読み込み)`

* 再送制御

<details>
<summary>keywords</summary>

MOMメッセージング, FwHeaderReader, MessageReader, 再送制御, データリーダ, mom_system_messaging

</details>

## 出力するデータの表示形式のフォーマット

データを出力する際に、 format を使用することで日付や数値などのデータの表示形式をフォーマットできる。
詳細は format を参照。

<details>
<summary>keywords</summary>

データフォーマット, 日付フォーマット, 数値フォーマット, format, 表示形式フォーマット

</details>
