**結論**: バリデーションエラー時のエラーメッセージは、`@OnError`アノテーションで遷移先JSPに戻し、JSPで`<n:errors>`タグや`<n:error>`タグを使って表示します。

**根拠**:

**1. アクション側 — `@InjectForm` + `@OnError` の設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // バリデーション通過後の業務処理
}
```

`@InjectForm`がバリデーションを実行し、エラー時に`ApplicationException`を送出します。`@OnError`が遷移先を指定します。`@OnError`を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必須です。

**2. JSPでのエラー表示**

全エラーを一覧表示する場合（`<n:errors>`タグ）:

```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

入力項目ごとに個別表示する場合（`<n:error>`タグ）:

```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <!-- 入力項目と同じ名前をname属性に指定する -->
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

グローバルメッセージ（項目に紐付かないメッセージ）のみ表示:

```jsp
<n:errors filter="global" errorCss="alert alert-danger" />
```

**3. Thymeleafを使う場合**

```html
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**4. エラーメッセージの定義（Bean Validationデフォルト設定）**

メッセージプロパティファイルにアノテーションのデフォルトメッセージIDをキーで定義します:

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
```

**5. コンポーネント設定でBean Validationを有効化**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**: `@OnError`が設定されていない場合、バリデーションエラーがシステムエラーとして処理されます。必ずアクションメソッドに設定してください。

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s16, libraries-tag.json:s29