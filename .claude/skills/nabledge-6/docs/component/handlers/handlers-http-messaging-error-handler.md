# HTTPメッセージングエラー制御ハンドラ

## 概要

本ハンドラでは後続のハンドラで発生した例外及びエラーを補足し、例外(エラー)に応じたログ出力とレスポンスの生成を行う。
また、後続のハンドラでレスポンスボディが設定されていない場合には、HTTPステータスコードに対応したデフォルトのボディをレスポンスに設定する。

本ハンドラでは、以下の処理を行う。

* 例外(エラー)に応じたログ出力とレスポンスの生成を行う。
詳細は、 例外の種類に応じたログ出力とレスポンス生成 を参照。

* デフォルトのレスポンスボディを設定する。
詳細は、 レスポンスボディが空の場合のデフォルトレスポンスの設定 を参照。

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-http-messaging-error-handler/flow.png)

## ハンドラクラス名

* `nablarch.fw.messaging.handler.HttpMessagingErrorHandler`

<details>
<summary>keywords</summary>

HttpMessagingErrorHandler, nablarch.fw.messaging.handler.HttpMessagingErrorHandler, ハンドラクラス

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging-http</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-fw-messaging-http, com.nablarch.framework, Mavenモジュール, 依存関係

</details>

## 制約

HTTPレスポンスハンドラ より後ろに配置すること
本ハンドラで生成した `HttpResponse` を HTTPレスポンスハンドラ が処理する。
このため、本ハンドラを HTTPレスポンスハンドラ より後ろに設定する必要がある。

<details>
<summary>keywords</summary>

http_response_handler, HttpResponse, ハンドラ配置順序, 制約

</details>

## 例外の種類に応じたログ出力とレスポンス生成

`nablarch.fw.NoMoreHandlerException`
:ログレベル: INFO
:レスポンス: 404
:説明: リクエストを処理すべきハンドラが存在しなかったことを意味するため、証跡ログとして記録する。
また、処理すべき *action class* が存在しなかったことを意味するため、HTTPステータスコードが *404*  のレスポンスを生成する。

`nablarch.fw.web.HttpErrorResponse`
:ログレベル: ログ出力なし
:レスポンス: `HttpErrorResponse#getResponse()`
:説明: 後続のハンドラで業務例外(バリデーションなどを行った結果の例外)が発生したことを意味するので、ログ出力は行わない。

`nablarch.fw.Result.Error`
:ログレベル: 設定による
:レスポンス: `Error#getStatusCode()`
:説明: nablarch.fw.Result.Errorのログ出力について を参照

`nablarch.core.message.ApplicationException` と `nablarch.fw.messaging.MessagingException`
:ログレベル: \-
:レスポンス: 400
:説明: クライアントからのリクエストが不正であることを示す例外のため、HTTPステータスコードが *400* のレスポンスを生成する。

上記以外の例外及びエラー
:ログレベル: FATAL
:レスポンス: 500
:説明: 上記に該当しない例外及びエラーの場合には、障害扱いとしてログ出力を行う。
また、予期しない例外やエラーであるため、レスポンスは **500** としている。

<details>
<summary>keywords</summary>

NoMoreHandlerException, HttpErrorResponse, Result.Error, ApplicationException, MessagingException, writeFailureLogPattern, ログ出力, レスポンス生成, 例外処理, エラーレスポンス

</details>

## nablarch.fw.Result.Errorのログ出力について

後続のハンドラで発生した例外が、 `Error` の場合はログ出力を行うかどうかは、
`writeFailureLogPattern` に設定した値によって変わる。
このプロパティには正規表現が設定でき、その正規表現が `Error#getStatusCode()` とマッチした場合に `FATAL` レベルのログを出力する。

## レスポンスボディが空の場合のデフォルトレスポンスの設定

詳細は、 HTTPエラー制御ハンドラのデフォルトページの設定 を参照。

<details>
<summary>keywords</summary>

HttpErrorHandler_DefaultPage, デフォルトレスポンスボディ, デフォルトページ, レスポンスボディ空

</details>
