Step 5: 回答を生成します。

---

**結論**: ウェブアプリケーションでバリデーションエラーのメッセージをユーザーに返すには、アクションに `@InjectForm` + `@OnError` を設定してエラー画面に遷移させ、JSP（`<n:errors>` / `<n:error>` タグ）または Thymeleaf（`ErrorMessages` オブジェクト）でエラーメッセージを表示します。

---

**根拠**:

### 1. アクション側の実装

アクションメソッドに `@InjectForm` と `@OnError` を組み合わせて設定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");

    // 業務処理
}
```

- `@InjectForm`: `form` プレフィックスのリクエストパラメータに対してバリデーションを実行し、エラーがなければフォームオブジェクトをリクエストスコープに格納します。
- `@OnError`: バリデーションエラー（`ApplicationException`）発生時に遷移する画面パスを指定します。`@OnError` がないとシステムエラー扱いになるため必須です。

### 2. コンポーネント設定（Bean Validation 使用時）

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 3. エラーメッセージの仕組み

`HTTPエラー制御ハンドラ` が `ApplicationException` を `ErrorMessages` に変換し、リクエストスコープのキー `errors` に格納します。

※キー名を変更したい場合:
```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 4. 画面でのエラーメッセージ表示

#### JSP（Nablarchカスタムタグ使用）

全エラーを一覧表示:
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

入力項目ごとに個別表示:
```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

#### Thymeleaf 使用時

特定プロパティのエラーを表示:
```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーを一覧表示:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

---

**注意点**:
- JSPカスタムタグはCSSフレームワークとの相性が悪い場合があります。その場合はリクエストスコープ上の `ErrorMessages` オブジェクトに直接アクセスする方法（Thymeleaf方式）が推奨されます。
- バリデーションエラー時にも入力値をリクエストスコープから参照したい場合は、`BeanValidationStrategy` の `copyBeanToRequestScopeOnError` を `true` に設定してください。

参照: `web-application-error-message.json`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `handlers-HttpErrorHandler.json:s4`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s16`, `libraries-tag.json:s29`

---