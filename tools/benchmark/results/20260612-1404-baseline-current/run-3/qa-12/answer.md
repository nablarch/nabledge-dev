**結論**: `@InjectForm` インターセプタがバリデーションを実行し、エラーが発生すると HTTPエラー制御ハンドラが `ApplicationException` のメッセージを `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に自動格納する。JSPでは `<n:errors>` / `<n:error>` タグ、Thymeleafでは `${errors.getMessage(...)}` などでエラーメッセージを表示できる。

---

**根拠**:

**① アクションへの設定**

業務アクションのメソッドに `@InjectForm` と `@OnError` を設定する。`@OnError` で遷移先を指定しないと、バリデーションエラーがシステムエラー扱いになる。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

**② JSPでのエラー表示（`n:errors` / `n:error` タグを使用）**

```jsp
<!-- すべてのエラーを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 特定項目のエラーを個別表示 -->
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**③ Thymeleafでのエラー表示**

HTTPエラー制御ハンドラがリクエストスコープの `errors` キーに `ErrorMessages` を格納するため、テンプレートから直接アクセスできる。

```html
<!-- 特定プロパティのエラーを表示 -->
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- すべてのエラーを一覧表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>

<!-- プロパティに紐付かないグローバルメッセージのみ表示 -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

---

**注意点**:
- `@OnError` が設定されていない場合、バリデーションエラーはシステムエラー扱いとなるため必ず設定すること
- リクエストスコープのキー名はデフォルトで `errors`。変更する場合はコンポーネント設定ファイルで `WebConfig` の `errorMessageRequestAttributeName` プロパティを設定する

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーをmessagesに変更 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-tag.json:s29