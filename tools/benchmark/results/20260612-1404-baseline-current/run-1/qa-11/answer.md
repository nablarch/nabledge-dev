**結論**: ウェブアプリケーションのエラー処理は主に `HttpErrorHandler`（HTTPエラー制御ハンドラ）が担い、例外の種類に応じてログ出力（ログレベル）とエラー画面への遷移（HTTPステータスコード）を制御する。

---

**根拠**:

## 1. ログ出力の仕組み（HTTPエラー制御ハンドラ）

後続ハンドラで発生した例外に対し、`HttpErrorHandler`（`nablarch.fw.web.handler.HttpErrorHandler`）が以下のようにログ出力とレスポンス生成を行う。

| 例外・エラーの種類 | ログレベル | HTTPレスポンス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし（業務例外） | `HttpErrorResponse#getResponse()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |
| `Result.Error` | `writeFailureLogPattern` 設定の正規表現に一致した場合 FATAL | `Error#getStatusCode()` |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー `errors` に設定する（JSPからアクセス可能）。

障害ログには2種類あり、それぞれ専用ロガーに出力する設計になっている：
- **障害通知ログ**: FATAL/ERROR レベル、ロガー名 `MONITOR`（監視ツール向け）
- **障害解析ログ**: FATAL/ERROR レベル、クラス名ロガー（アプリケーションログ）

## 2. エラー画面遷移の方法

方法は3つ提供されている：

### (A) HTTPエラー制御ハンドラでデフォルトページを設定
ステータスコードをエラーページにマッピングする設定（正規表現でのパターン指定が可能）：

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="404" value="/NOT_FOUND.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
    </map>
  </property>
</component>
```

> **注意**: デフォルトのエラーページ設定は `web.xml` の `error-page` 要素で行うことが推奨されている。

### (B) カスタムハンドラで例外クラスに応じた遷移先を定義
システム全体で共通のエラーページに遷移させたい場合はカスタムハンドラで対応する：

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context){
    try{
      return context.handleNext(data);
    } catch (NoDataException e){
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    } catch (OptimisticLockException e){
      throw new HttpErrorResponse(
          400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
    }
  }
}
```

### (C) アクションに `@OnError` アノテーションで指定
個別のアクションメソッドに対してエラー時の遷移先を指定する：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

---

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より後ろに配置する必要がある
- `GlobalErrorHandler`（グローバルエラーハンドラ）はハンドラキューの先頭に配置するが、これはウェブ・バッチ共通の汎用ハンドラ。ウェブアプリではエラー画面遷移に `HttpErrorHandler` が主役となる
- 個別アクションへの `@OnError` 指定は漏れやミスが生じやすいため、システム全体で統一する場合はカスタムハンドラ方式を推奨する

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, web-application-forward-error-page.json:s1, handlers-on-error.json:s3, libraries-failure-log.json:s1