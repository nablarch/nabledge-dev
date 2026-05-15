**結論**: バリデーションエラーが発生したとき、Nablarch 6 ではフレームワークが自動的に `ApplicationException` のメッセージを `ErrorMessages` オブジェクトに変換してリクエストスコープ（デフォルトキー名: `errors`）に格納します。テンプレート（Thymeleaf や JSP）でそのオブジェクトにアクセスしてエラーメッセージを表示します。

**根拠**:

全体の流れ（ウェブアプリケーションの場合）:
1. `@InjectForm` インターセプタが入力値をバリデーションし、エラーが発生すると `ApplicationException` を送出する。
2. `@OnError` インターセプタがその例外をキャッチし、指定された画面にフォワードする。
3. `HttpErrorHandler` が `ApplicationException` のメッセージを `ErrorMessages` に変換し、リクエストスコープに `errors` キーで格納する。
4. テンプレートがリクエストスコープの `errors` を参照してメッセージを表示する。

アクション側の実装例:
```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // ...
}
```

テンプレート（Thymeleaf）でのエラーメッセージ表示例:
特定プロパティのメッセージを表示：
```html
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```
全エラーメッセージを一覧表示：
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

エラーメッセージ定義（Bean Validation使用時）:
```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

RESTfulウェブサービスの場合: `@Valid` アノテーションをリソースメソッドに設定してバリデーションします。エラーメッセージをレスポンスボディに含めるには、`ErrorResponseBuilder` を継承したカスタムクラスで `ApplicationException` 発生時の JSON レスポンスを実装します。

**注意点**:
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー（500）扱いになるため、`@InjectForm` と必ず対で設定すること。
- リクエストスコープのエラーキー名は、テンプレート側と設定ファイルで一致させること（デフォルト: `errors`）。
- Bean Validation のフォームプロパティは全て `String` 型で定義すること。
- RESTful API ではデフォルトのエラーレスポンスボディは空になるため、エラーメッセージを返したい場合は `ErrorResponseBuilder` のカスタマイズが必要。

参照: `processing-pattern/web-application/web-application-error-message.json`, `component/handlers/handlers-HttpErrorHandler.json#s4`, `component/handlers/handlers-InjectForm.json#s3`, `component/handlers/handlers-InjectForm.json#s4`, `component/handlers/handlers-on-error.json#s3`, `component/libraries/libraries-bean-validation.json#s7`, `component/handlers/handlers-jaxrs-bean-validation-handler.json#s4`, `component/handlers/handlers-jaxrs-response-handler.json#s7`