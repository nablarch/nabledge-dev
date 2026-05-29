セクション内容が揃いました。Step 5〜8を実行します。

---

**結論**: `@InjectForm` + `@OnError` インターセプタでバリデーションエラー時の遷移先を指定し、HTTPエラー制御ハンドラが `ApplicationException` のメッセージを `errors` キーでリクエストスコープに格納します。画面側（JSPまたはThymeleaf）ではそのスコープ変数を参照してエラーメッセージを表示します。

**根拠**:

### 1. アクション側の実装

業務アクションのメソッドに `@InjectForm`（バリデーション実行）と `@OnError`（エラー時の遷移先）を設定します。

**Bean Validationを使う場合のコンポーネント設定（XML）:**
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**業務アクションの実装例:**
```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーションが通った場合のみここに到達する
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う。
}
```

`@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになるため必ず設定してください。

### 2. エラーメッセージのリクエストスコープへの格納（フレームワーク自動処理）

`HTTPエラー制御ハンドラ`（`nablarch.fw.web.handler.HttpErrorHandler`）が以下を自動処理します：

1. `ApplicationException` のメッセージ情報を `ErrorMessages` に変換
2. `ErrorMessages` をリクエストスコープにキー名 `errors` で設定（デフォルト）

キー名を変更したい場合は以下のように設定します：
```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 3. 画面側の表示

**Thymeleafを使う場合:**

特定の入力項目のエラーを表示：
```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーを一覧表示：
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**JSPカスタムタグを使う場合:**

全エラー一覧表示（`n:errors` タグ）：
```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

入力項目ごとの個別表示（`n:error` タグ）：
```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**注意点**:
- `@OnError` の設定を忘れるとバリデーションエラーがシステムエラー（500）として扱われます。
- JSPカスタムタグ（`n:errors`/`n:error`）はDOM構造の制約によりCSSフレームワークとの相性が悪い場合があります。その場合はリクエストスコープの `errors` オブジェクト（`ErrorMessages`）に直接アクセスする方式を検討してください。
- エラー時の遷移先画面でDBからプルダウン選択肢などを取得する必要がある場合は、`@OnError` の `path` に `forward://` を使って初期表示用メソッドに内部フォワードします。

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-tag.json:s29, libraries-bean-validation.json:s16, handlers-on-error.json:s3, handlers-on-error.json:s4

---