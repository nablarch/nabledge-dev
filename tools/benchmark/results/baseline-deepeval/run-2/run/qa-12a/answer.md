**結論**: ウェブアプリケーションでの入力チェックエラー時は、業務アクションに`@InjectForm`と`@OnError`アノテーションを組み合わせて設定し、JSPなら`<n:errors>` / `<n:error>`カスタムタグ、Thymeleafなら`ErrorMessages`オブジェクト経由でエラーメッセージをユーザーに表示する。

---

**根拠**:

**1. 業務アクション側の設定**

`@InjectForm`でバリデーションを実行し、`@OnError`でエラー時の遷移先を指定する。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // バリデーション済みフォームをリクエストスコープから取得
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

> **注意**: `@OnError`が設定されていない場合、バリデーションエラーがシステムエラー扱いになる。

Bean Validationを使う場合、コンポーネント設定ファイルに以下を追加する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. JSPでのエラーメッセージ表示**

全エラーメッセージ一覧表示:

```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

入力項目ごとの個別表示:

```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**3. Thymeleafでのエラーメッセージ表示**

HTTPエラー制御ハンドラがバリデーションエラーをリクエストスコープの`errors`に格納する。`ErrorMessages`オブジェクトを使って表示できる。

特定プロパティのエラーを表示:

```html
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージを表示:

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**4. エラーメッセージの定義**

メッセージはプロパティファイルにアノテーションのデフォルトメッセージIDをキーに定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:
- JSPカスタムタグはリクエストスコープの`ApplicationException`を参照するため、`@OnError`または`@OnErrors`インターセプタとの併用が必須。
- エラー時の遷移先画面でプルダウン選択肢など初期表示データが必要な場合は、`path = "forward://initializeRegisterPage"` のように内部フォワードを使用する。

参照: web-application-error-message.json:s1, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s16, libraries-bean-validation.json:s7, libraries-tag.json:s29, handlers-on-error.json:s3

---