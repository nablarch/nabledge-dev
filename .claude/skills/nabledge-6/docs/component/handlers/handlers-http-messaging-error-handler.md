# HTTPメッセージングエラー制御ハンドラ

**目次**

* ハンドラクラス名
* モジュール一覧
* 制約
* 例外の種類に応じたログ出力とレスポンス生成

  * nablarch.fw.Result.Errorのログ出力について
* レスポンスボディが空の場合のデフォルトレスポンスの設定

本ハンドラでは後続のハンドラで発生した例外及びエラーを補足し、例外(エラー)に応じたログ出力とレスポンスの生成を行う。
また、後続のハンドラでレスポンスボディが設定されていない場合には、HTTPステータスコードに対応したデフォルトのボディをレスポンスに設定する。

本ハンドラでは、以下の処理を行う。

* 例外(エラー)に応じたログ出力とレスポンスの生成を行う。
  詳細は、 例外の種類に応じたログ出力とレスポンス生成 を参照。
* デフォルトのレスポンスボディを設定する。
  詳細は、 レスポンスボディが空の場合のデフォルトレスポンスの設定 を参照。

処理の流れは以下のとおり。

![](../images/HttpMessagingErrorHandler/flow.png)

## ハンドラクラス名

* nablarch.fw.messaging.handler.HttpMessagingErrorHandler

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging-http</artifactId>
</dependency>
```

## 制約

HTTPレスポンスハンドラ より後ろに配置すること
本ハンドラで生成した HttpResponse を HTTPレスポンスハンドラ が処理する。
このため、本ハンドラを HTTPレスポンスハンドラ より後ろに設定する必要がある。

## 例外の種類に応じたログ出力とレスポンス生成

nablarch.fw.NoMoreHandlerException
nablarch.fw.web.HttpErrorResponse
nablarch.fw.Result.Error
nablarch.core.message.ApplicationException と nablarch.fw.messaging.MessagingException
上記以外の例外及びエラー

## nablarch.fw.Result.Errorのログ出力について

後続のハンドラで発生した例外が、 Error の場合はログ出力を行うかどうかは、
writeFailureLogPattern に設定した値によって変わる。
このプロパティには正規表現が設定でき、その正規表現が Error#getStatusCode() とマッチした場合に FATAL レベルのログを出力する。

## レスポンスボディが空の場合のデフォルトレスポンスの設定

詳細は、 HTTPエラー制御ハンドラのデフォルトページの設定 を参照。
