# 機能詳細

**公式ドキュメント**: [1](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/web_service/http_messaging/feature_details.html) [2](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/messaging/action/MessagingAction.html)

## Nablarchの初期化

:ref:`ウェブアプリケーションのNablarchの初期化 <web_feature_details-nablarch_initialization>` を参照。

*キーワード: Nablarch初期化, ウェブアプリケーション初期化, web_feature_details-nablarch_initialization*

## 入力値のチェック

- :ref:`入力値のチェック <validation>`

*キーワード: 入力値チェック, バリデーション, validation*

## データベースアクセス

- :ref:`データベースアクセス <database_management>`

*キーワード: データベースアクセス, database_management*

## 排他制御

- :ref:`universal_dao`
  - :ref:`universal_dao_jpa_optimistic_lock`
  - :ref:`universal_dao_jpa_pessimistic_lock`

> **重要**: :ref:`exclusive_control` 機能はクライアント（taglib）との連動が前提であるため、HTTPメッセージングでは使用できない。

*キーワード: 排他制御, 楽観的排他制御, 悲観的排他制御, UniversalDao, universal_dao_jpa_optimistic_lock, universal_dao_jpa_pessimistic_lock, exclusive_control使用不可*

## URIとアクションクラスのマッピング

- :ref:`http_request_java_package_mapping`

> **補足**: HTTPメッセージングでは :ref:`router_adaptor` を使用できない。HTTPメッセージングは :ref:`mom_system_messaging` が提供する `MessagingAction` でアクションクラスを作成するため、URIに応じてアクションクラスのメソッドを呼び分ける想定がない。

*キーワード: URIマッピング, アクションクラス, MessagingAction, mom_system_messaging, router_adaptor使用不可, http_request_java_package_mapping*

## 国際化対応

- :ref:`メッセージの多言語化 <message-multi_lang>`
- :ref:`コード名称の多言語化 <code-use_multilingualization>`

*キーワード: 国際化, 多言語化, メッセージ多言語化, コード名称多言語化*

## 認証

認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。

*キーワード: 認証, フレームワーク未提供, プロジェクト要件*

## 認可チェック

- :ref:`permission_check`

*キーワード: 認可チェック, permission_check, パーミッションチェック*

## エラー時に返却するレスポンス

- :ref:`http_messaging_error_handler`

*キーワード: エラーレスポンス, http_messaging_error_handler, エラーハンドラ*
