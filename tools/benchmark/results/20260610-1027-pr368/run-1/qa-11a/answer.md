**結論**: ウェブアプリケーションでのエラー処理は、主に「`HttpErrorHandler`（HTTPエラー制御ハンドラ）」「`@OnError`/`@OnErrors` アノテーション」「障害ログ出力機能」の3層で構成されます。例外の種類に応じて自動的にログレベルが決まり、エラー画面への遷移先もハンドラまたはアノテーションで制御します。

---

**根拠**:

#### 1. ログ出力の仕組み（HttpErrorHandler）

ハンドラキュー後段で発生した例外は `HttpErrorHandler` がキャッチし、例外の種類によってログレベルとHTTPステータスコードを自動的に決定します。

| 例外クラス | ログ | ステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `getResponse()` の値 |
| `Result.Error` | `writeFailureLogPattern` に一致すれば FATAL | `getStatusCode()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージをリクエストスコープ（キー名: `errors`）に設定します。これにより JSP 側でエラーメッセージを表示できます。

#### 2. エラー画面の遷移方法

**方法1: アクションメソッドに `@OnError` アノテーション**

例外の種類ごとに遷移先を指定します。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理は省略
}
```

複数の例外に対応するには `@OnErrors` を使います。継承関係がある場合はサブクラスを先に定義する必要があります。

```java
@OnErrors({
        @OnError(type = UserLockedException.class, path = "/WEB-INF/view/login/locked.jsp"),
        @OnError(type = AuthenticationException.class, path = "/WEB-INF/view/login/index.jsp"),
        @OnError(type = ApplicationException.class, path = "/WEB-INF/view/login/index.jsp")
})
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

**方法2: 共通ハンドラで全体を制御**

システム全体で遷移先を統一したい場合は、個別アノテーションではなくカスタムハンドラを追加します。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
    @Override
    public Object handle(Object data, ExecutionContext context) {
        try {
            return context.handleNext(data);
        } catch (NoDataException e) {
            throw new HttpErrorResponse(
                404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
        } catch (OptimisticLockException e) {
            throw new HttpErrorResponse(
                400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
        }
    }
}
```

**方法3: `HttpErrorHandler` でステータスコード別デフォルトページを設定**

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

ただし、デフォルトページの設定は `web.xml` の `error-page` 要素で行うことが推奨されています。

#### 3. 障害ログの出力方針

障害ログは2種類に分かれます。

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL、ERROR | `MONITOR` |
| 障害解析ログ（アプリケーションログ） | FATAL、ERROR | クラス名 |

アプリケーションから明示的に障害ログを出力する場合は `FailureLogUtil` を使用します。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

フレームワークの例外ハンドラ（`GlobalErrorHandler` など）が例外をキャッチした場合は、障害コードの指定がない場合でも設定済みのデフォルト障害コードとメッセージで自動的に障害ログが出力されます。

---

**注意点**:
- `@OnErrors` で継承関係にある例外を定義する場合、必ずサブクラスを先に定義してください（順序通りに処理されるため）。
- `HttpErrorHandler` の `defaultPages` 機能を使う場合、`web.xml` の `error-page` 要素にも同様の設定が必要です（設定しない場合、エラーの発生場所によってはウェブサーバのデフォルトエラーページが表示されます）。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-on-error.json:s3, handlers-on-errors.json:s3, libraries-failure-log.json:s1, libraries-failure-log.json:s3, web-application-forward-error-page.json:s1