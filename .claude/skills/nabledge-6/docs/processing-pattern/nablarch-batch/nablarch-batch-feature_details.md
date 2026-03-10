# 機能詳細

**公式ドキュメント**: [1](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/nablarch_batch/feature_details.html) [2](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/reader/DatabaseRecordReader.html) [3](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/reader/FileDataReader.html) [4](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/reader/ValidatableFileDataReader.html) [5](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/reader/ResumeDataReader.html)

## バッチアプリケーションの起動方法

- :ref:`Nablarchバッチアプリケーションの起動方法<main-run_application>`

<small>キーワード: バッチアプリケーション起動, Nablarchバッチ起動方法, アプリケーション実行</small>

## システムリポジトリの初期化

システムリポジトリの初期化は、アプリケーション起動時にシステムリポジトリの設定ファイルのパスを指定することで行う。

<small>キーワード: システムリポジトリ初期化, 設定ファイルパス指定, アプリケーション起動時初期化</small>

## 入力値のチェック

- :ref:`入力値のチェック <validation>`

<small>キーワード: 入力値チェック, バリデーション, validation</small>

## データベースアクセス

:ref:`データベースアクセス <database_management>`

標準提供のデータリーダ:
- `DatabaseRecordReader (データベース読み込み)`

<small>キーワード: データベースアクセス, DatabaseRecordReader, データリーダ, データベース読み込み</small>

## ファイル入出力

:ref:`ファイル入出力<data_converter>`

標準提供のデータリーダ:
- `FileDataReader (ファイル読み込み)`
- `ValidatableFileDataReader (バリデージョン機能付きファイル読み込み)`
- `ResumeDataReader (レジューム機能付き読み込み)`

<small>キーワード: ファイル入出力, FileDataReader, ValidatableFileDataReader, ResumeDataReader, ファイル読み込み, レジューム機能</small>

## 排他制御

排他制御は2種類の方法を提供するが、:ref:`UniversalDaoを推奨する理由 <exclusive_control-deprecated>` に記載の通り、:ref:`universal_dao` の使用を推奨する。

- :ref:`exclusive_control`
- :ref:`universal_dao`
  - :ref:`悲観的ロック<nablarch_batch_pessimistic_lock>`

<small>キーワード: 排他制御, UniversalDao推奨, 悲観的ロック, exclusive_control非推奨, pessimistic lock</small>

## バッチ処理の実行制御

- :ref:`バッチ処理のプロセス終了コード<status_code_convert_handler-rules>`
- :ref:`バッチ処理のエラー処理<nablarch_batch_error_process>`
- :ref:`バッチ処理の並列実行(マルチスレッド化)<multi_thread_execution_handler>`
- :ref:`バッチ処理のコミット間隔の制御 <loop_handler-commit_interval>`
- :ref:`1回のバッチ処理の処理件数制限 <data_read_handler-max_count>` (大量データを処理するバッチ処理を数日に分けて処理させる場合など)

<small>キーワード: バッチ実行制御, プロセス終了コード, エラー処理, マルチスレッド並列実行, コミット間隔, 処理件数制限</small>

## MOMメッセージ送信

- :ref:`同期応答メッセージ送信<mom_system_messaging-sync_message_send>`
- :ref:`応答不要メッセージ送信<mom_system_messaging-async_message_send>`

<small>キーワード: MOMメッセージ送信, 同期応答メッセージ送信, 応答不要メッセージ送信, メッセージング</small>

## バッチ実行中の状態の保持

- :ref:`nablarch_batch_retention_state`

<small>キーワード: バッチ状態保持, バッチ実行中状態, nablarch_batch_retention_state</small>

## 常駐バッチのマルチプロセス化

- :ref:`nablarch_batch_multiple_process`

<small>キーワード: 常駐バッチ, マルチプロセス, nablarch_batch_multiple_process</small>
