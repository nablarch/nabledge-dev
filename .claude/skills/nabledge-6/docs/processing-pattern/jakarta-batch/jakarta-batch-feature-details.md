# 機能詳細

**目次**

* バッチアプリケーションの起動方法
* システムリポジトリの初期化
* バッチジョブに適用するリスナーの定義方法
* 入力値のチェック
* データベースアクセス
* ファイル入出力
* 排他制御
* ジョブ定義のxmlの作成方法
* MOMメッセージ送信
* 運用設計

## バッチアプリケーションの起動方法

feature_details/run_batch_application

* Jakarta Batchアプリケーションの起動方法

## システムリポジトリの初期化

* Jakarta Batchアプリケーションでシステムリポジトリの初期化

## バッチジョブに適用するリスナーの定義方法

* リスナーの定義方法

## 入力値のチェック

* 入力値のチェック

## データベースアクセス

feature_details/database_reader

* データベースアクセス
* database_reader

## ファイル入出力

* ファイル入出力

## 排他制御

feature_details/pessimistic_lock

排他制御は、以下の2種類の方法を提供しているが、
UniversalDaoを推奨する理由 に記載がある通り、
ユニバーサルDAO の使用を推奨する。

* 排他制御
* ユニバーサルDAO

  * 悲観的ロック

## ジョブ定義のxmlの作成方法

* [Jakarta Batch Specificationを参照(外部サイト、英語)](https://jakarta.ee/specifications/batch/)

## MOMメッセージ送信

* 同期応答メッセージ送信

## 運用設計

feature_details/operation_policy
feature_details/progress_log
feature_details/operator_notice_log

* operation_policy
* progress_log
* operator_notice_log
