**結論**: `@InjectForm` アノテーションでバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。バリデーションエラーは HTTPエラー制御ハンドラがリクエストスコープのキー `errors` に `ErrorMessages` として格納するため、JSPでは `n:errors`/`n:error` タグ、Thymeleafでは `errors.getMessage()` などでエラーメッセージを表示できる。

---

**根拠**:

**1. アクションメソッドに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション成功時のみここに到達する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う。
}
```

**2. Bean Validationを使うためのコンポーネント設定**

コンポーネント設定ファイルに `BeanValidationStrategy` を定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**3. エラーメッセージの表示（JSP）**

全エラーを一覧表示する場合は `n:errors` タグ、入力項目ごとに個別表示する場合は `n:error` タグを使用する。

```jsp
<!-- 全エラーメッセージを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 入力項目ごとに個別表示 -->
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**4. エラーメッセージの表示（Thymeleaf）**

リクエストスコープの `errors` から `ErrorMessages` にアクセスする。

```html
<!-- 特定プロパティのエラーを表示 -->
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーメッセージを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**5. エラーメッセージの定義（メッセージプロパティファイル）**

アノテーションのメッセージIDをキーにメッセージを定義する。アノテーション属性値をプレースホルダで埋め込める。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

---

**注意点**:
- `@OnError` を設定していない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- リクエストスコープのキー名はデフォルト `errors` だが、`WebConfig` の `errorMessageRequestAttributeName` プロパティで変更可能（変更例: `messages`）
- JSPカスタムタグ（`n:errors`/`n:error`）は `ApplicationException` をリクエストスコープから取得してメッセージを出力するため、DOM構造の制約がありCSSフレームワークとの相性が悪い場合がある。その場合はリクエストスコープ上の `ErrorMessages` に直接アクセスする方法を検討すること

参照: web-application-error-message.json:root, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s16, libraries-tag.json:s29, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s7

---