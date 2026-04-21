# 機能詳細

## バッチアプリケーションの起動方法

* Nablarchバッチアプリケーションの起動方法

<details>
<summary>keywords</summary>

バッチアプリケーション起動, Nablarchバッチ起動方法, アプリケーション実行

</details>

## システムリポジトリの初期化

システムリポジトリの初期化は、アプリケーション起動時にシステムリポジトリの設定ファイルのパスを指定することで行う。
詳細は、Nablarchバッチアプリケーションの起動方法 を参照。

<details>
<summary>keywords</summary>

システムリポジトリ初期化, 設定ファイルパス指定, アプリケーション起動時初期化

</details>

## 入力値のチェック

* 入力値のチェック

<details>
<summary>keywords</summary>

入力値チェック, バリデーション, validation

</details>

## データベースアクセス

* データベースアクセス
* 標準提供のデータリーダ

* `DatabaseRecordReader (データベース読み込み)`

<details>
<summary>keywords</summary>

データベースアクセス, DatabaseRecordReader, データリーダ, データベース読み込み

</details>

## ファイル入出力

* ファイル入出力

* 標準提供のデータリーダ

* `FileDataReader (ファイル読み込み)`
* `ValidatableFileDataReader (バリデージョン機能付きファイル読み込み)`
* `ResumeDataReader (レジューム機能付き読み込み)`

<details>
<summary>keywords</summary>

ファイル入出力, FileDataReader, ValidatableFileDataReader, ResumeDataReader, ファイル読み込み, レジューム機能

</details>

## 排他制御

排他制御は、以下の2種類の方法を提供しているが、
UniversalDaoを推奨する理由 に記載がある通り、
ユニバーサルDAO の使用を推奨する。

* 排他制御
* ユニバーサルDAO

* 悲観的ロック

<details>
<summary>keywords</summary>

排他制御, UniversalDao推奨, 悲観的ロック, exclusive_control非推奨, pessimistic lock

</details>

## バッチ処理の実行制御

* バッチ処理のプロセス終了コード
* バッチ処理のエラー処理
* バッチ処理の並列実行(マルチスレッド化)
* バッチ処理のコミット間隔の制御
* 1回のバッチ処理の処理件数制限
|br| (大量データを処理するバッチ処理を数日に分けて処理させる場合など)

<details>
<summary>keywords</summary>

バッチ実行制御, プロセス終了コード, エラー処理, マルチスレッド並列実行, コミット間隔, 処理件数制限

</details>

## MOMメッセージ送信

* 同期応答メッセージ送信
* 応答不要メッセージ送信

<details>
<summary>keywords</summary>

MOMメッセージ送信, 同期応答メッセージ送信, 応答不要メッセージ送信, メッセージング

</details>

## バッチ実行中の状態の保持

* バッチアプリケーションで実行中の状態を保持する

<details>
<summary>keywords</summary>

バッチ状態保持, バッチ実行中状態, nablarch_batch_retention_state

</details>

## 常駐バッチのマルチプロセス化

* 常駐バッチアプリケーションのマルチプロセス化

.. |br| raw:: html

<br />

<details>
<summary>keywords</summary>

常駐バッチ, マルチプロセス, nablarch_batch_multiple_process

</details>
