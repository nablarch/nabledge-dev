**結論**: ウェブアプリケーションでバリデーションエラーのメッセージをユーザーに返すには、アクションメソッドに `@InjectForm` + `@OnError` アノテーションを設定し、テンプレート側でリクエストスコープの `errors` オブジェクト（`ErrorMessages`）を参照してメッセージを表示します。

**根拠**:

**① アクション側の実装**

バリデーションは `@InjectForm` インターセプタが担います。エラー発生時に入力画面へ戻るよう `@OnError` を必ず併用してください。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う。
}
```

**② エラーメッセージのリクエストスコープへの格納**

`ApplicationException` が発生すると、`HTTPエラー制御ハンドラ` がそれを `ErrorMessages` に変換し、リクエストスコープのキー `errors` に格納します。テンプレートはこの `errors` にアクセスしてメッセージを表示します（キー名はコンポーネント設定で変更可能）。

**③ テンプレートでのエラー表示（Thymeleafの例）**

特定の入力項目に対応したエラーを表示する場合:
```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージを一覧表示する場合:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（項目に紐付かないエラー）を表示する場合:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**④ JSP でのエラー表示（カスタムタグ使用）**

JSPを使用する場合は Nablarch カスタムタグが使えます。

全エラーを一覧表示:
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

項目ごとに個別表示:
```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**⑤ Bean Validation 使用時の追加設定**

`@InjectForm` で Bean Validation を使う場合、コンポーネント設定ファイルに以下を定義してください。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること。
- JSP カスタムタグ (`<n:errors>`, `<n:error>`) は出力する DOM 構造に制約があり、CSS フレームワークとの相性が悪い場合がある。その場合はリクエストスコープの `ErrorMessages` オブジェクトに直接アクセスする方式を検討すること。

参照: processing-pattern/web-application/web-application-error-message.json:s1, component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-bean-validation.json:s16, component/libraries/libraries-tag.json:s29