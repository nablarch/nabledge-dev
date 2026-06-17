**結論**: ウェブアプリケーションで入力チェックエラーをユーザーに返すには、①`@InjectForm` + `@OnError` でバリデーション実行とエラー画面遷移を設定し、②テンプレート（ThymeleafまたはJSP）でリクエストスコープの `ErrorMessages`（キー名: `errors`）にアクセスしてエラーメッセージを表示する。

**根拠**:

**Step 1: アクション側でバリデーションとエラー遷移先を設定**

`@InjectForm` アノテーションで入力値のバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。`@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必須。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

**Step 2: エラーメッセージの仕組み**

バリデーションエラー発生時、`HTTPエラー制御ハンドラ`が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープにキー名 `errors`（デフォルト）で設定する。

**Step 3: テンプレートでエラーメッセージを表示**

Thymeleafの場合:
```html
<!-- 特定プロパティのエラーメッセージを表示 -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- すべてのエラーメッセージを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>

<!-- グローバルメッセージ（プロパティに紐付かない）を表示 -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

JSP（Nablarchカスタムタグ）の場合:
```jsp
<!-- すべてのエラーメッセージを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 特定項目のエラーメッセージを個別表示 -->
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**エラーメッセージの定義**: `@InjectForm` で Bean Validation を使う場合、メッセージはプロパティファイルで定義する（デフォルトで `NablarchMessageInterpolator` がメッセージ管理を使用）。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**Bean Validation のコンポーネント設定**（`@InjectForm` で Bean Validation を使う場合に必要）:
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- `@OnError` が設定されていないとバリデーションエラーがシステムエラー扱いになる
- リクエストスコープのキー名はデフォルト `errors`。変更する場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定
- JSPカスタムタグはDOM構造の制約によりCSSフレームワークと相性が悪いことがある。Thymeleafなどでリクエストスコープに直接アクセスする方法が推奨

参照: component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-bean-validation.json:s7, component/libraries/libraries-bean-validation.json:s16, component/libraries/libraries-tag.json:s29