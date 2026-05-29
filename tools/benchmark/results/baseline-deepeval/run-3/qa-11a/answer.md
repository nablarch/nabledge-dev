十分な情報が集まりました。回答を生成します。

---

**結論**: ウェブアプリケーションでのエラー処理は、主に **HTTPエラー制御ハンドラ（`HttpErrorHandler`）** が中心的な役割を担い、例外の種類に応じたログ出力とエラーページへの遷移を制御します。個別アクションのエラー遷移先は **`@OnError` インターセプタ**、システム共通のエラー遷移は **カスタムハンドラ** で制御します。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

後続ハンドラで発生した例外を捕捉し、ログ出力とエラー用 `HttpResponse` の生成を行います。

| 例外の種類 | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse` が持つレスポンスを使用 |
| `Result.Error` | 設定による（`writeFailureLogPattern`で制御） | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

**バリデーションエラー（`ApplicationException`）時の特別処理**:
`HttpErrorResponse` の原因例外が `ApplicationException` の場合、メッセージ情報を `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に設定します。これによりビュー側でエラーメッセージを表示できます。

**エラーページのデフォルト設定（`defaultPages`）**:
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
> ただし、デフォルトエラーページの設定は `web.xml` で行うことを推奨しています。

---

### 2. 個別アクションのエラー遷移先：`@OnError` インターセプタ

業務アクションメソッドに `@OnError` を付与することで、特定の例外が発生した際の遷移先を指定できます。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

---

### 3. システム共通のエラー遷移：カスタムハンドラ

全機能で共通のエラーページに遷移させたい場合は、ハンドラを追加して制御します（`@OnError` を個別に指定すると漏れが発生するリスクがあるため）。

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

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置する必要があります。
- `@OnError` は単一の例外に対して1つの遷移先しか指定できません。複数の遷移先が必要な場合は `try-catch` で個別に `HttpErrorResponse` を生成します。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-on-error.json:s3, web-application-forward-error-page.json:s1, web-application-forward-error-page.json:s2

---