**結論**: Nablarchでは、エラー発生時のエラー画面表示は `HttpErrorHandler`（HTTPエラー制御ハンドラ）と `@OnError` インターセプタが担い、ログ出力はハンドラが自動的に行う障害ログ機能（`FailureLogUtil`）が担う。例外の種類に応じてログレベルとHTTPステータスコードが自動的に振り分けられる。

**根拠**:

### 1. エラー画面表示の仕組み

**HTTPエラー制御ハンドラ（`HttpErrorHandler`）** がハンドラキューに配置され、後続ハンドラで発生したすべての例外を捕捉してエラーレスポンスを生成する。例外の種類に応じた処理：

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `getResponse()`の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージをリクエストスコープ（デフォルトキー `errors`）に設定するため、Viewでエラーメッセージを扱える。

デフォルトエラーページの設定例：
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

アクションレベルでの遷移先指定（`@OnError` インターセプタ）：
```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

システム全体で共通のエラーページに遷移させる場合は専用ハンドラを追加する：
```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context) {
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    }
  }
}
```

### 2. ログ出力の仕組み

**グローバルエラーハンドラ（`GlobalErrorHandler`）** はハンドラキューの先頭に配置し、未捕捉の例外・エラーを捕捉してログ出力する。

フレームワークでは2種類の障害ログを出力する：

| ログの種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | ログ監視ツール向け専用ファイルに出力 |
| 障害解析ログ | FATAL/ERROR | クラス名 | アプリケーション全体のログファイルに出力 |

アプリケーションからの障害ログ出力：
```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

**注意点**:
- `HttpErrorHandler` は HTTPレスポンスハンドラより後ろに配置する必要がある
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること（それより手前で例外が発生するとJVMやWebサーバが処理する）
- エラー画面のデフォルトページ設定は `web.xml` の `error-page` 要素を使う方が推奨されている
- `HttpErrorResponse` の原因例外が `ApplicationException` の場合のみリクエストスコープにエラーメッセージが設定される

参照: `component/handlers/handlers-HttpErrorHandler.json#s4`, `component/handlers/handlers-HttpErrorHandler.json#s6`, `component/handlers/handlers-global-error-handler.json#s4`, `component/libraries/libraries-failure-log.json#s1`, `component/libraries/libraries-failure-log.json#s3`, `processing-pattern/web-application/web-application-forward-error-page.json#s1`, `component/handlers/handlers-on-error.json#s3`, `component/libraries/libraries-log.json#s3`