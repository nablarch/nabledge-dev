読み込んだセクション内容から回答を生成します。

---

**結論**: `@InjectForm` + `@OnError` インターセプタでエラー遷移先を指定し、`HttpErrorHandler` がバリデーションエラーメッセージをリクエストスコープの `errors` キーに格納するので、JSP の `<n:error>` タグや Thymeleaf の `errors.getMessage()` でユーザーに表示する。

---

**根拠**:

**① コンポーネント設定（BeanValidationStrategy の登録）**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**② Form クラスの定義**

```java
public class UserForm {
    @Required
    @Length(max = 10)
    private String userName;
    // getter/setter は省略
}
```

**③ アクションへのインターセプタ設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

- バリデーションエラー発生時は `ApplicationException` がスローされ、`@OnError` で指定した遷移先（例: `registerForm.jsp`）にフォワードされる
- `HttpErrorHandler` が `ApplicationException` のメッセージを `ErrorMessages` に変換し、リクエストスコープの **`errors`** キーに格納する

**④ JSP でのエラー表示**

全エラーを一覧表示する場合（`<n:errors>` タグ）:

```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

入力項目の横に個別表示する場合（`<n:error>` タグ）:

```jsp
<div>
  <label>ユーザID</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**④'（Thymeleaf を使う場合）**

```html
<input type="text" name="form.userName" />
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

グローバルメッセージ（項目に紐づかないメッセージ）を表示する場合:

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**⑤ エラーメッセージのプロパティファイル定義**

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

---

**注意点**:
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- リクエストスコープのキー名はデフォルトで `errors`。変更する場合はコンポーネント設定で `WebConfig` の `errorMessageRequestAttributeName` プロパティを変更する
- JSP カスタムタグは DOM 構造の制約があるため、CSS フレームワークとの相性が悪い場合は Thymeleaf + `ErrorMessages` オブジェクト直接参照を検討する

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s16, libraries-tag.json:s29

---