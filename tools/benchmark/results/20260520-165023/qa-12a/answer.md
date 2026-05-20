**結論**: `@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。エラーメッセージは `HTTPエラー制御ハンドラ` によってリクエストスコープの `errors` キーに `ErrorMessages` として格納されるので、テンプレート（Thymeleaf または JSP カスタムタグ）からアクセスして表示する。

**根拠**:

### 1. アクション側の実装

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

`@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため注意。

### 2. Bean Validation を使う場合のコンポーネント設定

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 3. エラーメッセージの定義（プロパティファイル）

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

### 4. 画面でのエラー表示

**Thymeleaf を使う場合**（リクエストスコープの `errors` オブジェクトに直接アクセス）:

特定フィールドのエラーを表示:
```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージを一覧表示:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（項目に紐付かないメッセージ）を表示:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**JSP カスタムタグを使う場合**:

全エラーを一覧表示（`n:errors` タグ）:
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

フィールドごとに個別表示（`n:error` タグ）:
```jsp
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**注意点**:
- リクエストスコープのキー名はデフォルト `errors`。変更する場合はコンポーネント設定ファイルで `errorMessageRequestAttributeName` プロパティを指定する。
- JSP カスタムタグは DOM 構造の制約により CSS フレームワークとの相性が悪い場合がある。その場合はリクエストスコープオブジェクトへ直接アクセスする方式を使うと良い。

参照: processing-pattern/web-application/web-application-error-message.json:root, component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/handlers/handlers-on-error.json:s3, component/handlers/handlers-on-error.json:s4, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-tag.json:s29, component/libraries/libraries-bean-validation.json:s7, component/libraries/libraries-bean-validation.json:s16