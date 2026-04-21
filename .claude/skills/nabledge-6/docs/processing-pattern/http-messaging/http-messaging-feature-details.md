# 機能詳細

## Nablarchの初期化

ウェブアプリケーションのNablarchの初期化 を参照。

<details>
<summary>keywords</summary>

Nablarch初期化, ウェブアプリケーション初期化, web_feature_details-nablarch_initialization

</details>

## 入力値のチェック

* 入力値のチェック

<details>
<summary>keywords</summary>

入力値チェック, バリデーション, validation

</details>

## データベースアクセス

* データベースアクセス

<details>
<summary>keywords</summary>

データベースアクセス, database_management

</details>

## 排他制御

* ユニバーサルDAO

* universal_dao_jpa_optimistic_lock
* universal_dao_jpa_pessimistic_lock


> **Important:** 排他制御 機能は、クライアント(taglib)との連動が前提であるため、 HTTPメッセージングでは使用できない。

<details>
<summary>keywords</summary>

排他制御, 楽観的排他制御, 悲観的排他制御, UniversalDao, universal_dao_jpa_optimistic_lock, universal_dao_jpa_pessimistic_lock, exclusive_control使用不可

</details>

## URIとアクションクラスのマッピング

* HTTPリクエストディスパッチハンドラ

> **Tip:** HTTPメッセージングでは ルーティングアダプタ を使用できない。 HTTPメッセージングは、MOMメッセージング が提供する extdoc:`MessagingAction<nablarch.fw.messaging.action.MessagingAction>` でアクションクラスを作成するため、URIに応じてアクションクラスのメソッドを呼び分ける想定がないため。

<details>
<summary>keywords</summary>

URIマッピング, アクションクラス, MessagingAction, mom_system_messaging, router_adaptor使用不可, http_request_java_package_mapping

</details>

## 国際化対応

静的リソースの多言語化対応については以下を参照。

* メッセージの多言語化
* コード名称の多言語化

<details>
<summary>keywords</summary>

国際化, 多言語化, メッセージ多言語化, コード名称多言語化

</details>

## 認証

認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。

<details>
<summary>keywords</summary>

認証, フレームワーク未提供, プロジェクト要件

</details>

## 認可チェック

* permission_check

<details>
<summary>keywords</summary>

認可チェック, permission_check, パーミッションチェック

</details>

## エラー時に返却するレスポンス

* HTTPメッセージングエラー制御ハンドラ

<details>
<summary>keywords</summary>

エラーレスポンス, http_messaging_error_handler, エラーハンドラ

</details>
