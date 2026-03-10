# 機能詳細

**公式ドキュメント**: [機能詳細](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/web/feature_details.html)

## Nablarchの初期化

Nablarchの初期化には以下の2つの設定が必要:

1. :ref:`システムリポジトリのロードの為の設定 <nablarch_servlet_context_listener>`
2. :ref:`ハンドラキューの設定(構築) <web_front_controller>`

*キーワード: nablarch_servlet_context_listener, web_front_controller, Nablarch初期化, システムリポジトリ, ハンドラキュー設定*

## 入力値のチェック

- :ref:`入力値のチェック <validation>`
- [エラーメッセージの画面表示](web-application-error_message.md)

*キーワード: validation, バリデーション, 入力値チェック, エラーメッセージ*

## データベースアクセス

データベースアクセス: :ref:`database_management`

*キーワード: database_management, データベースアクセス, DB操作*

## 排他制御

排他制御は2種類提供されるが、:ref:`universal_dao` の使用を推奨する（:ref:`UniversalDaoを推奨する理由 <exclusive_control-deprecated>` 参照）。

- :ref:`exclusive_control`
- :ref:`universal_dao`（推奨）
  - :ref:`universal_dao_jpa_optimistic_lock`（楽観排他）
  - :ref:`universal_dao_jpa_pessimistic_lock`（悲観排他）

*キーワード: exclusive_control, universal_dao, universal_dao_jpa_optimistic_lock, universal_dao_jpa_pessimistic_lock, 排他制御, 楽観排他, 悲観排他*

## ファイルアップロード

ファイルアップロードの読み込み: :ref:`multipart_handler-read_upload_file`

*キーワード: multipart_handler-read_upload_file, ファイルアップロード, マルチパート*

## ファイルダウンロード

ファイルダウンロードは2種類提供されるが、:ref:`data_bind` の使用を推奨する（:ref:`データバインドを推奨する理由 <data_converter-data_bind_recommend>` 参照）。

- :ref:`データバインド機能を使用したファイルダウンロード <data_bind-file_download>`（推奨）
- :ref:`汎用データフォーマット機能を使用したファイルダウンロード <data_format-file_download>`

> **警告**: 大量データのダウンロード時は :ref:`universal_dao-lazy_load` を使用し、データベースの検索結果をヒープ上に展開しないこと。

*キーワード: data_bind, data_bind-file_download, data_format-file_download, universal_dao-lazy_load, ファイルダウンロード, データバインド, 大量データ*

## URIとアクションクラスのマッピング

URIとアクションクラスのマッピングは2種類提供されるが、:ref:`router_adaptor` の使用を推奨する（:ref:`ルーティングアダプタが推奨である理由 <http_request_java_package_mapping-router_adaptor>` 参照）。

- :ref:`router_adaptor`（推奨）
- :ref:`http_request_java_package_mapping`

*キーワード: router_adaptor, http_request_java_package_mapping, URIマッピング, アクションクラスマッピング, ルーティング*

## 2重サブミット防止

2重サブミット防止: :ref:`2重サブミット防止 <tag-double_submission>`

JSP以外のテンプレートエンジンを使用する場合は :ref:`use_token_interceptor` も参照すること。

*キーワード: tag-double_submission, use_token_interceptor, 2重サブミット防止, ダブルサブミット*

## 入力データの保持

入力データの保持: :ref:`session_store`

*キーワード: session_store, セッションストア, 入力データ保持*

## ページネーション

データベースから範囲を指定して検索する方法は :ref:`database_management` を参照。

クライアントサイドのページネーションはプロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。

*キーワード: database_management, ページネーション, 範囲検索, クライアントサイドページング*

## 画面の作成

**JSPを使用する場合:**
- :ref:`JSPのtaglibを使用した画面開発 <tag>`
- :ref:`jsp_session`

**JSP以外のテンプレートエンジンを使用する場合:**
- :ref:`Thymeleafを使用した画面開発 <web_thymeleaf_adaptor>`
- :ref:`view_other`

*キーワード: tag, jsp_session, web_thymeleaf_adaptor, view_other, JSP, Thymeleaf, 画面開発, テンプレートエンジン*

## 国際化対応

**静的リソースの多言語化:**
- :ref:`メッセージの多言語化 <message-multi_lang>`
- :ref:`コード名称の多言語化 <code-use_multilingualization>`

**言語切り替えの2通りの方法:**
- :ref:`メッセージタグでの国際化対応 <tag-write_message>`
- :ref:`言語ごとにリソースのパスを切り替える <tag_change_resource_path_of_lang>`

> **警告**: :ref:`メッセージタグでの国際化対応 <tag-write_message>` を使用した場合、画面レイアウトが崩れる可能性がある。レイアウト崩れを許容できる場合のみ使用すること。

*キーワード: message-multi_lang, code-use_multilingualization, tag-write_message, tag_change_resource_path_of_lang, 国際化, 多言語化, 言語切り替え*

## 認証

認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装すること。

認証情報の保持: :ref:`session_store-authentication_data`

*キーワード: session_store-authentication_data, 認証, 認証情報*

## 認可チェック

認可チェック: :ref:`permission_check`

*キーワード: permission_check, 認可チェック, 権限チェック*

## ステータスコード

[ステータスコードの使い分け(外部サイト)](https://qiita.com/kawasima/items/e48180041ace99842779)

*キーワード: ステータスコード, HTTPステータスコード*

## エラー時の画面遷移とステータスコード

エラー時の画面遷移とステータスコードの設定方法:

1. :ref:`ステータスコードに対応したデフォルトの遷移先ページを設定する <HttpErrorHandler_DefaultPage>`
2. :ref:`ハンドラで例外クラスに対応したエラーページに遷移させる <forward_error_page-handler>`
3. アクションでエラー時の遷移先を指定する:
   - 例外クラスに対応した遷移先を定義する（:ref:`on_error_interceptor`、:ref:`on_errors_interceptor`）
   - :ref:`1つの例外に対して複数の遷移先を定義する <forward_error_page-try_catch>`

[ステータスコードの使い分け(外部サイト)](https://qiita.com/kawasima/items/e48180041ace99842779)

*キーワード: HttpErrorHandler_DefaultPage, forward_error_page-handler, on_error_interceptor, on_errors_interceptor, forward_error_page-try_catch, エラーページ遷移, エラーハンドリング*

## MOMメッセージ送信

MOMメッセージ送信: :ref:`同期応答メッセージ送信 <mom_system_messaging-sync_message_send>`

*キーワード: mom_system_messaging-sync_message_send, MOMメッセージ, 同期応答メッセージ送信*

## Webアプリケーションのスケールアウト設計

Webアプリケーションのスケールアウト設計: :ref:`stateless_web_app`

*キーワード: stateless_web_app, スケールアウト, ステートレス, 水平スケール*

## CSRF対策

CSRF対策: :ref:`CSRF対策 <csrf_token_verification_handler>`

*キーワード: csrf_token_verification_handler, CSRF対策, CSRFトークン, クロスサイトリクエストフォージェリ*

## ウェブアプリケーションとRESTfulウェブサービスの併用

ウェブアプリケーションとRESTfulウェブサービスを併用する場合: :ref:`委譲するWebフロントコントローラの名前を変更する <change_web_front_controller_name>`

*キーワード: change_web_front_controller_name, Webフロントコントローラ, RESTfulウェブサービス併用*

## Content Security Policy(CSP)対応

Content Security Policy(CSP)対応: :ref:`Content Security Policy(CSP)対応 <content_security_policy>`

*キーワード: content_security_policy, CSP, Content Security Policy*
