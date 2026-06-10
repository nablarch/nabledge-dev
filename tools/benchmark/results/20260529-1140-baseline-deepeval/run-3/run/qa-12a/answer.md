**結論**: `@InjectForm` + `@OnError` でバリデーションエラー時の遷移先を指定し、HTTPエラー制御ハンドラがエラーメッセージをリクエストスコープ(`errors`)に格納するので、テンプレートエンジンから `ErrorMessages` を参照して画面に表示します。

---

**根拠**:

**1. バリデーションの設定（コンポーネント定義）**

BeanValidationStrategy を `validationStrategy` という名前で定義する必要があります。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. 業務アクションの実装**

`@InjectForm` でバリデーションを有効にし、`@OnError` でエラー時の遷移先を指定します。`@OnError` がない場合、バリデーションエラーがシステムエラー扱いになるため必須です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う
}
```

**3. エラーメッセージのリクエストスコープへの格納**

HTTPエラー制御ハンドラが `ApplicationException` を検知すると、エラーメッセージを `ErrorMessages` に変換し、リクエストスコープのキー名 `errors`（デフォルト値）で格納します。

**4. テンプレートエンジンでのエラー表示（Thymeleafの例）**

特定プロパティのエラーメッセージを表示する場合:

```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのエラーメッセージを一覧表示する場合:

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（特定プロパティに紐付かないメッセージ）を表示する場合:

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**5. エラーメッセージの定義**

バリデーションアノテーションに対応するメッセージはプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

---

**注意点**:
- JSPを使う場合、カスタムタグ(`<n:errors>`)でも表示できますが、CSSフレームワークとの相性が悪い場合があります。リクエストスコープの `errors` オブジェクトに直接アクセスする方が柔軟に対応できます。
- リクエストスコープのキー名はデフォルトで `errors` ですが、コンポーネント設定で変更可能です。

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s16

---