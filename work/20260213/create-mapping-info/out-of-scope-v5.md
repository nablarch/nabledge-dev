# Out of Scope Files - V5

This document lists all files excluded from scope with their reasons.

## Summary

- **Total out-of-scope files**: 72
- **Exclusion reasons**: 6

## Exclusion Reasons

1. [DB Messaging (Resident Batch) excluded per specification](#db-messaging-resident-batch-excluded-per-specification) (8 files)
2. [Jakarta Batch excluded per specification](#jakarta-batch-excluded-per-specification) (13 files)
3. [MOM Messaging excluded per specification](#mom-messaging-excluded-per-specification) (5 files)
4. [Messaging excluded per specification](#messaging-excluded-per-specification) (1 files)
5. [Test files and tooling excluded](#test-files-and-tooling-excluded) (1 files)
6. [Web applications (JSP/UI) excluded per specification](#web-applications-jspui-excluded-per-specification) (44 files)

## DB Messaging (Resident Batch) excluded per specification

**Total files**: 8

### アプリケーションの責務配置

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/application_design.rst`
- **Categories**: None

### アーキテクチャ概要

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/architecture.rst`
- **Categories**: None

### 機能詳細

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/feature_details.rst`
- **Categories**: None

### データベースをキューとしたメッセージングのエラー処理

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/feature_details/error_processing.rst`
- **Categories**: None

### マルチプロセス化

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/feature_details/multiple_process.rst`
- **Categories**: None

### Getting Started

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/getting_started.rst`
- **Categories**: None

### テーブルキューを監視し未処理データを取り込むアプリケーションの作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/getting_started/table_queue.rst`
- **Categories**: None

### テーブルをキューとして使ったメッセージング

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/db/index.rst`
- **Categories**: None

## Jakarta Batch excluded per specification

**Total files**: 13

### アプリケーションの責務配置

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/application_design.rst`
- **Categories**: None

### アーキテクチャ概要

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/architecture.rst`
- **Categories**: None

### 機能詳細

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details.rst`
- **Categories**: None

### データベースを入力とするChunkステップ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst`
- **Categories**: None

### 運用方針

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/operation_policy.rst`
- **Categories**: None

### 運用担当者向けのログ出力

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/operator_notice_log.rst`
- **Categories**: None

### JSR352に準拠したバッチアプリケーションの悲観的ロック

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/pessimistic_lock.rst`
- **Categories**: None

### 進捗状況のログ出力

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/progress_log.rst`
- **Categories**: None

### JSR352バッチアプリケーションの起動

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/feature_details/run_batch_application.rst`
- **Categories**: None

### 対象テーブルのデータを削除するバッチの作成(Batchletステップ)

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/getting_started/batchlet/index.rst`
- **Categories**: None

### データを導出するバッチの作成(Chunkステップ)

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/getting_started/chunk/index.rst`
- **Categories**: None

### Getting Started

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/getting_started/getting_started.rst`
- **Categories**: None

### JSR352に準拠したバッチアプリケーション

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/batch/jsr352/index.rst`
- **Categories**: None

## MOM Messaging excluded per specification

**Total files**: 5

### アプリケーションの責務配置

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/mom/application_design.rst`
- **Categories**: None

### アーキテクチャ概要

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/mom/architecture.rst`
- **Categories**: None

### 機能詳細

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/mom/feature_details.rst`
- **Categories**: None

### Getting Started

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/mom/getting_started.rst`
- **Categories**: None

### MOMによるメッセージング

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/mom/index.rst`
- **Categories**: None

## Messaging excluded per specification

**Total files**: 1

### メッセージング編

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/messaging/index.rst`
- **Categories**: None

## Test files and tooling excluded

**Total files**: 1

### textlintのテスト

- **File**: `nab-official/v5/nablarch-document/.textlint/test/test.rst`
- **Categories**: None

## Web applications (JSP/UI) excluded per specification

**Total files**: 44

### HTTPエラー制御ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/HttpErrorHandler.rst`
- **Categories**: None

### セッション変数保存ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/SessionStoreHandler.rst`
- **Categories**: None

### CSRFトークン検証ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/csrf_token_verification_handler.rst`
- **Categories**: None

### 内部フォーワードハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/forwarding_handler.rst`
- **Categories**: None

### ヘルスチェックエンドポイントハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/health_check_endpoint_handler.rst`
- **Categories**: None

### ホットデプロイハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/hot_deploy_handler.rst`
- **Categories**: None

### HTTPアクセスログハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/http_access_log_handler.rst`
- **Categories**: None

### HTTP文字エンコード制御ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/http_character_encoding_handler.rst`
- **Categories**: None

### HTTPリクエストディスパッチハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/http_request_java_package_mapping.rst`
- **Categories**: None

### HTTPレスポンスハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/http_response_handler.rst`
- **Categories**: None

### HTTPリライトハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/http_rewrite_handler.rst`
- **Categories**: None

### ウェブアプリケーション専用ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/index.rst`
- **Categories**: None

### 携帯端末アクセスハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/keitai_access_handler.rst`
- **Categories**: None

### マルチパートリクエストハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/multipart_handler.rst`
- **Categories**: None

### Nablarchカスタムタグ制御ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/nablarch_tag_handler.rst`
- **Categories**: None

### ノーマライズハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/normalize_handler.rst`
- **Categories**: None

### POST再送信防止ハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/post_resubmit_prevent_handler.rst`
- **Categories**: None

### リソースマッピングハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/resource_mapping.rst`
- **Categories**: None

### セキュアハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/secure_handler.rst`
- **Categories**: None

### セッション並行アクセスハンドラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/handlers/web/session_concurrent_access_handler.rst`
- **Categories**: None

### アプリケーションの責務配置

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/application_design.rst`
- **Categories**: None

### アーキテクチャ概要

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/architecture.rst`
- **Categories**: None

### 機能詳細

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details.rst`
- **Categories**: None

### バリデーションエラーのメッセージを画面表示する

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/error_message.rst`
- **Categories**: None

### エラー時の遷移先の指定方法

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/forward_error_page.rst`
- **Categories**: None

### JSPで自動的にHTTPセッションを作成しないようにする方法

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/jsp_session.rst`
- **Categories**: None

### Nablarchサーブレットコンテキスト初期化リスナー

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/nablarch_servlet_context_listener.rst`
- **Categories**: None

### FreeMarkerを使用した画面開発

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/view/freemarker.rst`
- **Categories**: None

### その他のテンプレートエンジンを使用した画面開発

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/view/other.rst`
- **Categories**: None

### Webフロントコントローラ

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/feature_details/web_front_controller.rst`
- **Categories**: None

### 登録画面初期表示の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/client_create1.rst`
- **Categories**: None

### 登録内容の確認

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/client_create2.rst`
- **Categories**: None

### 登録内容確認画面から登録画面へ戻る

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/client_create3.rst`
- **Categories**: None

### データベースへの登録

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/client_create4.rst`
- **Categories**: None

### 登録機能の作成(ハンズオン形式)

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/index.rst`
- **Categories**: None

### Getting Started

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/index.rst`
- **Categories**: None

### ポップアップ画面の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/popup/index.rst`
- **Categories**: None

### 一括更新機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_bulk_update/index.rst`
- **Categories**: None

### 削除機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_delete/index.rst`
- **Categories**: None

### ファイルダウンロード機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_download/index.rst`
- **Categories**: None

### 検索機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_search/index.rst`
- **Categories**: None

### 更新機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_update/index.rst`
- **Categories**: None

### アップロードを用いた一括登録機能の作成

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/getting_started/project_upload/index.rst`
- **Categories**: None

### ウェブアプリケーション編

- **File**: `nab-official/v5/nablarch-document/ja/application_framework/application_framework/web/index.rst`
- **Categories**: None
