Step 5: 回答を生成します。

**結論**: `@InjectForm` インターセプタと `@OnError` アノテーションを業務アクションに設定し、バリデーションエラー時の遷移先画面で `ErrorMessages` オブジェクト（リクエストスコープのキー名: `errors`）からエラーメッセージを取得して表示します。

**根拠**:

**1. 業務アクションの実装**

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先を指定します。`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため注意が必要です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  // バリデーション済みのフォームをリクエストスコープから取得
  UserForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

**2. エラーメッセージの格納の仕組み**

`HTTPエラー制御ハンドラ` が、`ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー名 `errors` に設定します（キー名はコンポーネント設定で変更可能）。

**3. 画面でのエラーメッセージ表示（Thymeleaf の場合）**

特定プロパティのエラーを表示する:
```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのエラーを一覧表示する:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（プロパティに紐付かないメッセージ）を表示する:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**4. JSPの場合: カスタムタグを使う方法**

```jsp
<!-- エラーメッセージを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 特定項目のエラーを個別表示 -->
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**5. Bean Validation のメッセージ定義**

エラーメッセージはプロパティファイルにメッセージIDをキーとして定義します:

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

Bean Validation を使うにはコンポーネント設定ファイルに以下を定義します:
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなり、エラー画面へ遷移してしまいます。
- JSP カスタムタグ（`<n:errors>`等）はDOM構造の制約によりCSSフレームワークとの相性が悪い場合があります。そのような場合はリクエストスコープ上の `ErrorMessages` に直接アクセスする方法を検討してください。

参照: processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-bean-validation.json:s16, component/libraries/libraries-bean-validation.json:s7, component/libraries/libraries-tag.json:s29

---