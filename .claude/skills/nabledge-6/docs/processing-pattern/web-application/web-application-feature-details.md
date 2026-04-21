# 機能詳細

## Nablarchの初期化

Nablarchの初期化を行うためには、 システムリポジトリのロードの為の設定
及び ハンドラキューの設定(構築) が必要となる。

<details>
<summary>keywords</summary>

nablarch_servlet_context_listener, web_front_controller, Nablarch初期化, システムリポジトリ, ハンドラキュー設定

</details>

## 入力値のチェック

* 入力値のチェック
* エラーメッセージの画面表示

<details>
<summary>keywords</summary>

validation, バリデーション, 入力値チェック, エラーメッセージ

</details>

## データベースアクセス

* データベースアクセス

<details>
<summary>keywords</summary>

database_management, データベースアクセス, DB操作

</details>

## 排他制御

排他制御は、以下の2種類の方法を提供しているが、
UniversalDaoを推奨する理由 に記載がある通り、
ユニバーサルDAO の使用を推奨する。

* 排他制御
* ユニバーサルDAO

* universal_dao_jpa_optimistic_lock
* universal_dao_jpa_pessimistic_lock

<details>
<summary>keywords</summary>

exclusive_control, universal_dao, universal_dao_jpa_optimistic_lock, universal_dao_jpa_pessimistic_lock, 排他制御, 楽観排他, 悲観排他

</details>

## ファイルアップロード

* アップロードしたファイルを読み込む

<details>
<summary>keywords</summary>

multipart_handler-read_upload_file, ファイルアップロード, マルチパート

</details>

## ファイルダウンロード

ファイルダウンロードは、以下の2種類の方法を提供しているが、
データバインドを推奨する理由 に記載がある通り、
データバインド の使用を推奨する。

* データバインド機能を使用したファイルダウンロード
* 汎用データフォーマット機能を使用したファイルダウンロード

大量データのダウンロード時には、 検索結果を遅延ロードする を参照し、
データベースの検索結果をヒープ上に展開しないように注意すること。

<details>
<summary>keywords</summary>

data_bind, data_bind-file_download, data_format-file_download, universal_dao-lazy_load, ファイルダウンロード, データバインド, 大量データ

</details>

## URIとアクションクラスのマッピング

以下の2種類の方法を提供しているが、
ルーティングアダプタが推奨である理由 に記載がある通り、 ルーティングアダプタ の使用を推奨する。

* ルーティングアダプタ
* HTTPリクエストディスパッチハンドラ

<details>
<summary>keywords</summary>

router_adaptor, http_request_java_package_mapping, URIマッピング, アクションクラスマッピング, ルーティング

</details>

## 2重サブミット防止

* 2重サブミット防止

また、JSP以外のテンプレートエンジンを使用している場合は UseTokenインターセプタ も参照すること。

<details>
<summary>keywords</summary>

tag-double_submission, use_token_interceptor, 2重サブミット防止, ダブルサブミット

</details>

## 入力データの保持

* session_store

<details>
<summary>keywords</summary>

session_store, セッションストア, 入力データ保持

</details>

## ページネーション

データベースから範囲を指定して検索する方法は、 データベースアクセス を参照。

クライアントサイドについては、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。

<details>
<summary>keywords</summary>

database_management, ページネーション, 範囲検索, クライアントサイドページング

</details>

## 画面の作成

* JSPを使用する場合

* JSPのtaglibを使用した画面開発
* JSPで自動的にHTTPセッションを作成しないようにする方法

* JSP以外のテンプレートエンジンを使用する場合

* Thymeleafを使用した画面開発
* その他のテンプレートエンジンを使用した画面開発

<details>
<summary>keywords</summary>

tag, jsp_session, web_thymeleaf_adaptor, view_other, JSP, Thymeleaf, 画面開発, テンプレートエンジン

</details>

## 国際化対応

静的リソースの多言語化対応については以下を参照。

* メッセージの多言語化
* コード名称の多言語化

画面表示する文言の言語を切り替えるには、以下の2通りの方法を提供しているが、
メッセージタグでの国際化対応 を使用した場合、
画面レイアウトが崩れる可能性がある。
そのため、レイアウト崩れを許容できる場合のみ、 メッセージタグでの国際化対応 を使用すること。

* メッセージタグでの国際化対応
* 言語ごとにリソースのパスを切り替える

<details>
<summary>keywords</summary>

message-multi_lang, code-use_multilingualization, tag-write_message, tag_change_resource_path_of_lang, 国際化, 多言語化, 言語切り替え

</details>

## 認証

認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。
プロジェクト要件に合わせてPJで実装する。

認証情報の保持については、以下を参照。

* session_store-authentication_data

<details>
<summary>keywords</summary>

session_store-authentication_data, 認証, 認証情報

</details>

## 認可チェック

* permission_check

<details>
<summary>keywords</summary>

permission_check, 認可チェック, 権限チェック

</details>

## ステータスコード

* [ステータスコードの使い分け(外部サイト)](https://qiita.com/kawasima/items/e48180041ace99842779)

<details>
<summary>keywords</summary>

ステータスコード, HTTPステータスコード

</details>

## エラー時の画面遷移とステータスコード

* ステータスコードに対応したデフォルトの遷移先ページを設定する
* ハンドラで例外クラスに対応したエラーページに遷移させる
* アクションでエラー時の遷移先を指定する

* 例外クラスに対応した遷移先を定義する (OnErrorインターセプタ 、 OnErrorsインターセプタ)
* 1つの例外に対して複数の遷移先を定義する
* [ステータスコードの使い分け(外部サイト)](https://qiita.com/kawasima/items/e48180041ace99842779)

<details>
<summary>keywords</summary>

HttpErrorHandler_DefaultPage, forward_error_page-handler, on_error_interceptor, on_errors_interceptor, forward_error_page-try_catch, エラーページ遷移, エラーハンドリング

</details>

## MOMメッセージ送信

* 同期応答メッセージ送信

<details>
<summary>keywords</summary>

mom_system_messaging-sync_message_send, MOMメッセージ, 同期応答メッセージ送信

</details>

## Webアプリケーションのスケールアウト設計

* stateless_web_app

<details>
<summary>keywords</summary>

stateless_web_app, スケールアウト, ステートレス, 水平スケール

</details>

## CSRF対策

* CSRF対策

<details>
<summary>keywords</summary>

csrf_token_verification_handler, CSRF対策, CSRFトークン, クロスサイトリクエストフォージェリ

</details>

## ウェブアプリケーションとRESTfulウェブサービスの併用

* 委譲するWebフロントコントローラの名前を変更する

<details>
<summary>keywords</summary>

change_web_front_controller_name, Webフロントコントローラ, RESTfulウェブサービス併用

</details>

## Content Security Policy(CSP)対応

* Content Security Policy(CSP)対応

<details>
<summary>keywords</summary>

content_security_policy, CSP, Content Security Policy

</details>
