**結論**: ウェブアプリケーションでバリデーションエラー時にエラーメッセージをユーザーに返すには、業務アクションに `@InjectForm` と `@OnError` アノテーションを組み合わせ、JSPではカスタムタグ（`<n:error>` / `<n:errors>`）またはリクエストスコープの `ErrorMessages` オブジェクトを使って画面にメッセージを表示します。

---

**根拠**:

**1. サーバーサイド：アクションの実装**

業務アクションのメソッドに `@InjectForm`（入力値チェック）と `@OnError`（エラー時の遷移先指定）を設定します。`@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため注意が必要です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  // バリデーション済みのフォームをリクエストスコープから取得
  UserForm form = ctx.getRequestScopedVar("form");
  // 業務処理...
}
```

Bean Validationを使う場合は、コンポーネント設定ファイルに `BeanValidationStrategy` を定義する必要があります。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. エラーメッセージの定義**

`@Length` などのアノテーションに対するメッセージはプロパティファイルに定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**3. 画面側：エラーメッセージの表示**

バリデーションエラーメッセージはHTTPエラー制御ハンドラによってリクエストスコープに格納されます。

**JSP（カスタムタグ使用）の場合:**

- すべてのエラーを一覧表示（`<n:errors>`）:
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

- 項目ごとに個別表示（`<n:error>`）:
```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**Thymeleaf使用の場合:**

リクエストスコープの `ErrorMessages` オブジェクトに直接アクセスします。

```html
<!-- 特定項目のエラーメッセージ -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーメッセージ一覧 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- `@OnError` を設定していないと、バリデーションエラーがシステムエラーとして扱われる
- JSPカスタムタグはDOM構造の制約によりCSSフレームワークとの相性が悪い場合がある。その場合はリクエストスコープの `ErrorMessages` を直接参照する方法を検討すること
- エラー時の遷移先画面でプルダウン選択肢などのデータが必要な場合は、`@OnError` の `path` に内部フォワード（`forward://`）を使用して初期表示メソッドに委譲する

参照: `web-application-error-message.json`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s16`, `libraries-tag.json:s29`, `handlers-on-error.json:s3`, `handlers-on-error.json:s4`

---