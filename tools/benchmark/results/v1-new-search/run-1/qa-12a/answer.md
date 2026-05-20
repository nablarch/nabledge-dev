**結論**: `@InjectForm` + `@OnError` で入力チェックを実行してエラー時の遷移先を設定し、遷移先の JSP（または Thymeleaf テンプレート）でリクエストスコープの `errors` オブジェクトからメッセージを表示する。

**根拠**:

**1. アクション側の実装（InjectForm + OnError）**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーションが通った場合のみここに到達
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

- `@InjectForm` でリクエストパラメータのバリデーションを実行する
- `@OnError` でバリデーションエラー（`ApplicationException`）発生時の遷移先を指定する
- `@OnError` を設定しない場合はバリデーションエラーがシステムエラー扱いとなるため注意

**2. エラーメッセージのリクエストスコープへの格納（HttpErrorHandler）**

`HttpErrorHandler` が `ApplicationException` を `ErrorMessages` に変換してリクエストスコープに設定する。デフォルトのキー名は `errors`（`WebConfig#errorMessageRequestAttributeName` で変更可能）。

**3. 画面側の表示（JSP カスタムタグ）**

全エラーを一覧表示する場合：
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

特定の入力項目に対応するエラーを個別表示する場合：
```jsp
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**4. Thymeleaf を使用する場合**

特定プロパティのエラーを表示する場合：
```html
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーを表示する場合：
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- JSP カスタムタグ（`<n:errors>`）を使うと DOM 構造の制約により CSS フレームワークとの相性が悪い場合がある。その場合はリクエストスコープの `ErrorMessages` オブジェクトに直接アクセスする方法を検討すること

参照: component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-tag.json:s29, processing-pattern/web-application/web-application-error-message.json