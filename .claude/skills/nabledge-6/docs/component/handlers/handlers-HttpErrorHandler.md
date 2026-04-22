# HTTPエラー制御ハンドラ

**目次**

* ハンドラクラス名
* モジュール一覧
* 制約
* 例外の種類に応じた処理とレスポンスの生成

  * nablarch.fw.Result.Errorのログ出力について
* デフォルトページの設定

後続のハンドラで発生した例外に対するログ出力やレスポンスへの変換を行うハンドラ。

本ハンドラでは、以下の処理を行う。

* 例外の種類に応じたログ出力
* 例外の種類に応じたエラー用HttpResponseの生成と返却
* デフォルトページの設定

処理の流れは以下のとおり。

![](../images/HttpErrorHandler/flow.png)

## ハンドラクラス名

* nablarch.fw.web.handler.HttpErrorHandler

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

## 制約

HTTPレスポンスハンドラ より後ろに配置すること
本ハンドラで生成した HttpResponse をHTTPレスポンスハンドラが処理するため、
本ハンドラは HTTPレスポンスハンドラ より後ろに配置する必要がある。
HTTPアクセスログハンドラ より後ろに配置すること
本ハンドラで生成したエラー用 HttpResponse を元にログ出力を行うため、
HTTPアクセスログハンドラ より後ろに配置する必要がある。

## 例外の種類に応じた処理とレスポンスの生成

nablarch.fw.NoMoreHandlerException
nablarch.fw.web.HttpErrorResponse
nablarch.fw.Result.Error
java.lang.StackOverflowError
java.lang.ThreadDeath と java.lang.VirtualMachineError ( java.lang.StackOverflowError 以外)
上記以外の例外及びエラー

## nablarch.fw.Result.Errorのログ出力について

後続のハンドラで発生した例外が、 Error の場合はログ出力を行うかどうかは、
writeFailureLogPattern に設定した値によって変わる。
このプロパティには正規表現が設定でき、その正規表現が Error#getStatusCode() とマッチした場合に FATAL レベルのログを出力する。

## デフォルトページの設定

後続のハンドラや本ハンドラのエラー処理で作成した HttpResponse に対して、デフォルトページを適用する。
この機能では、 HttpResponse が設定されていなかった場合、
defaultPage や
defaultPages で設定されたデフォルトのページを適用する。

以下に設定例を示す。

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="404" value="/NOT_FOUND.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
      <entry key="503" value="/NOT_IN_SERVICE.jsp" />
    </map>
  </property>
</component>
```

> **Important:**
> この機能を使用した場合、Servlet APIで規定されている web.xml へのエラーページ設定( error-page 要素)と重複してJSPの設定が必要となる。
> web.xml へ設定しなかった場合、エラーの発生場所によっては、ウェブサーバのデフォルトのエラーページが表示される。

> このため、本機能を使用するのではなく、デフォルトのエラーページの設定は、 web.xml へ行うことを推奨する。
