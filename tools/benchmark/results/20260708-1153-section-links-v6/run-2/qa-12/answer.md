**結論**: ウェブアプリケーションでは、業務アクションのメソッドに `@InjectForm` と `@OnError` アノテーションを設定する。バリデーションエラー発生時、HTTPエラー制御ハンドラが `ApplicationException` をキャッチして `ErrorMessages` オブジェクトをリクエストスコープ（デフォルトキー: `errors`）に格納するため、テンプレート側でこのオブジェクトを使ってエラーメッセージを表示できる。

---

**根拠**:

**① アクションクラスの実装**

業務アクションのメソッドに `@InjectForm` と `@OnError` を設定する。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みのフォームをリクエストスコープから取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなる。

**② Bean Validation 使用時のコンポーネント設定**

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**③ 画面側でのエラーメッセージ表示（Thymeleaf 使用例）**

HTTPエラー制御ハンドラが `ApplicationException` を処理し、`ErrorMessages` をリクエストスコープのキー `errors` に格納する。テンプレート側でこれを参照する。

特定プロパティのエラーを表示:
```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージを表示:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（プロパティに紐付かないメッセージ）を表示:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

---

**注意点**:
- `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになる
- エラーメッセージのリクエストスコープキー名はデフォルトで `errors`。変更する場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定する
- FormクラスのプロパティはすべてString型として定義すること（型変換はバリデーション後に行う）
- JSPを使用する場合は Nablarch カスタムタグの `<n:errors>` タグでもエラー表示が可能だが、DOM構造の制約からCSSフレームワークとの相性が悪い場合がある

参照:
- バリデーションエラーのメッセージを画面表示する
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-error-message.md
- InjectForm インターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md
  InjectFormを使用する
  バリデーションエラー時の遷移先を指定する
- HTTPエラー制御ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md
  例外の種類に応じた処理とレスポンスの生成
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションエラー時のエラーメッセージを定義する
  ウェブアプリケーションのユーザ入力値のチェックを行う