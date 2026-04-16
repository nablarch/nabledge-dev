# 機能詳細

## 概要

## Nablarchの初期化

ウェブアプリケーションのNablarchの初期化 を参照。

## 入力値のチェック

* 入力値のチェック

## データベースアクセス

* データベースアクセス

## 排他制御

* universal_dao

* universal_dao_jpa_optimistic_lock
* universal_dao_jpa_pessimistic_lock

> **Important:** RESTfulウェブサービスでは `ETag` や `If-Match` を使用した楽観的ロックには対応していない。 そのため、RESTfulウェブサービスで楽観的ロックを行う際は、リクエストボディに直接バージョン番号を含めること。
> **Important:** `exclusive_control` 機能は、クライアント(taglib)との連動が前提であるため、 RESTfulウェブサービスでは使用できない。

## URIとリソース(アクション)クラスのマッピング

* router_adaptor
* リソースクラスのメソッドのシグネチャ

## パスパラメータやクエリーパラメータ

* rest_feature_details-path_param
* rest_feature_details-query_param

## レスポンスヘッダ

* リソースクラスのメソッドで個別にレスポンスヘッダを設定する
* jaxrs_response_handler-response_finisher

## 国際化対応

静的リソースの多言語化対応については以下を参照。

* メッセージの多言語化
* コード名称の多言語化

## 認証

認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。

## 認可チェック

認可チェックについては、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。

## エラー時に返却するレスポンス

* jaxrs_response_handler-error_response_body
* jaxrs_response_handler-individually_error_response

## Webアプリケーションのスケールアウト設計

* stateless_web_app

## CSRF対策

* CSRF対策

## CORS

* CORS

## OpenAPIドキュメントからのソースコード生成

* nablarch_openapi_generator
