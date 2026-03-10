# 機能詳細

**公式ドキュメント**: [機能詳細](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/jsr352/feature_details.html)

## バッチアプリケーションの起動方法

- :ref:`Jakarta Batchアプリケーションの起動方法 <jsr352_run_batch_application>`

*キーワード: Jakarta Batchアプリケーション起動, バッチ起動方法, jsr352_run_batch_application*

## システムリポジトリの初期化

- :ref:`Jakarta Batchアプリケーションでシステムリポジトリの初期化 <jsr352_run_batch_init_repository>`

*キーワード: システムリポジトリ初期化, Jakarta Batchシステムリポジトリ, jsr352_run_batch_init_repository*

## バッチジョブに適用するリスナーの定義方法

- :ref:`リスナーの定義方法 <jsr352-listener_definition>`

*キーワード: リスナー定義, バッチジョブリスナー, jsr352-listener_definition*

## 入力値のチェック

- :ref:`入力値のチェック <validation>`

*キーワード: 入力値チェック, バリデーション, validation*

## データベースアクセス

- :ref:`データベースアクセス <database_management>`
- [feature_details/database_reader](jakarta-batch-database_reader.md)

*キーワード: データベースアクセス, database_management, database_reader, DatabaseReader*

## ファイル入出力

- :ref:`ファイル入出力<data_converter>`

*キーワード: ファイル入出力, data_converter, ファイル読み書き*

## 排他制御

排他制御は2種類の方法を提供しているが、:ref:`UniversalDaoを推奨する理由 <exclusive_control-deprecated>` に記載がある通り、:ref:`universal_dao` の使用を推奨する。

- :ref:`exclusive_control`
- :ref:`universal_dao`
  - [悲観的ロック](jakarta-batch-pessimistic_lock.md)

*キーワード: 排他制御, UniversalDao, 悲観的ロック, exclusive_control, universal_dao, ペシミスティックロック*

## ジョブ定義のxmlの作成方法

[Jakarta Batch Specificationを参照(外部サイト、英語)](https://jakarta.ee/specifications/batch/)

*キーワード: ジョブ定義XML, Jakarta Batch Specification, ジョブXML作成*

## MOMメッセージ送信

- :ref:`同期応答メッセージ送信<mom_system_messaging-sync_message_send>`

*キーワード: MOMメッセージ送信, 同期応答メッセージ送信, mom_system_messaging*

## 運用設計

- [feature_details/operation_policy](jakarta-batch-operation_policy.md)
- [feature_details/progress_log](jakarta-batch-progress_log.md)
- [feature_details/operator_notice_log](jakarta-batch-operator_notice_log.md)

*キーワード: 運用設計, 進捗ログ, オペレーター通知ログ, operation_policy, progress_log, operator_notice_log*
