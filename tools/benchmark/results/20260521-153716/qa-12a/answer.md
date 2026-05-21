セクション内容が揃いました。回答を生成します。

---

**結論**: `@InjectForm` + `@OnError` アノテーションでバリデーションを実行してエラー時の遷移先を設定し、テンプレート側でリクエストスコープの `errors`（`ErrorMessages`）オブジェクトにアクセスしてエラーメッセージを表示する。

**根拠**:

**① アクション側の実装（`@InjectForm` + `@OnError`）**

`@InjectForm` アノテーションで入力値のバリデーションを実行する。`@OnError` でバリデーションエラー時の遷移先を指定する（設定しないとシステムエラー扱いになる点に注意）。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // バリデーション済みフォームで業務処理
}
```

**② ハンドラによるエラーメッセージの格納**

`HTTPエラー制御ハンドラ` が `ApplicationException` を受け取り、メッセージ情報を `ErrorMessages` に変換してリクエストスコープに設定する。デフォルトのキー名は `errors`。

キー名を変更したい場合はコンポーネント設定ファイルで変更できる：

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

**③ テンプレート（Thymeleaf）でのエラー表示**

特定のプロパティのエラーを表示する:
```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーを表示する:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**④ Bean Validationを使う場合の設定**

`BeanValidationStrategy` をコンポーネント設定ファイルに定義する：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**⑤ エラーメッセージの定義**

メッセージはプロパティファイルにアノテーションのデフォルトメッセージIDをキーとして定義する：

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `@OnError` を設定しないと `ApplicationException` がシステムエラー扱いになるため、必ず設定すること
- JSPを使用する場合、カスタムタグ（`<n:errors>`）を使う方法もあるが、DOM構造の制約によりCSSフレームワークとの相性が悪い問題がある。リクエストスコープの `errors` オブジェクトに直接アクセスする方法も選択肢となる

参照: handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s16

---