# 機能詳細

## アプリケーションの起動方法

DBメッセージングのアプリケーション起動方法は、Nablarchの共通の起動方法に従う。詳細は :ref:`アプリケーションの起動方法<main-run_application>` を参照。

## システムリポジトリの初期化

アプリケーション起動時にシステムリポジトリの設定ファイルのパスを指定することで初期化する。詳細は :ref:`アプリケーションの起動方法<main-run_application>` を参照。

## データベースアクセス

- :ref:`データベースアクセス <database_management>`
- 標準提供のデータリーダ: `DatabaseTableQueueReader (データベースのテーブルをキューとして扱うリーダ)`

## 入力値のチェック

DBメッセージングにおける入力値のチェックは、Nablarchの標準的なバリデーション機能を使用する。詳細は :ref:`入力値のチェック <validation>` を参照。

## 排他制御

排他制御は2種類提供されているが、:ref:`UniversalDaoを推奨する理由 <exclusive_control-deprecated>` に記載の通り、:ref:`universal_dao` の使用を推奨する。

- :ref:`exclusive_control`
- :ref:`universal_dao`
  - :ref:`universal_dao_jpa_pessimistic_lock`

## 実行制御

- :ref:`プロセス終了コード<status_code_convert_handler-rules>`
- :ref:`エラー発生データを除外して処理を継続する <db_messaging-exclude_error_data>`
- :ref:`メッセージングプロセスを異常終了させる <db_messaging-process_abnormal_end>`
- :ref:`処理の並列実行(マルチスレッド化)<multi_thread_execution_handler>`

## マルチプロセス化

DBメッセージングの処理を複数プロセスで並列実行する方法を提供する。詳細は :ref:`db_messaging-multiple_process` を参照。
