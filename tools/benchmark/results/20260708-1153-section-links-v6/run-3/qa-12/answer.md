**結論**: ウェブアプリケーションでバリデーションエラーのメッセージをユーザーに返すには、業務アクションに `@InjectForm` と `@OnError` アノテーションを設定し、テンプレートエンジン（Thymeleafなど）のViewでリクエストスコープに格納された `ErrorMessages` オブジェクトにアクセスしてエラーメッセージを表示する。

**根拠**:

**1. バリデーションの設定（コンポーネント定義）**

Bean Validationを使う場合、コンポーネント設定ファイルに `BeanValidationStrategy` を定義する必要がある。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. 業務アクションでのバリデーション実行**

`@InjectForm` アノテーションでバリデーションを実行し、`@OnError` でエラー時の遷移先画面を指定する。`@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため必須。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  // バリデーション済みフォームをリクエストスコープから取得
  UserForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う
}
```

**3. エラーメッセージのリクエストスコープへの自動格納**

バリデーションエラー発生時、HTTPエラー制御ハンドラが `ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー `errors`（デフォルト）に自動格納する。

**4. テンプレートエンジン（Thymeleaf）でのエラーメッセージ表示**

```html
<!-- 特定のプロパティのエラーメッセージを表示 -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全メッセージを一覧表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>

<!-- グローバルメッセージ（プロパティに紐付かないメッセージ）を表示 -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラーとなる。
- JSPを使う場合はNablarchカスタムタグ（`<n:errors>`）でも表示できるが、DOM構造の制約によりCSSフレームワークとの相性が悪い場合がある。その場合はリクエストスコープ上の `ErrorMessages` オブジェクトに直接アクセスする方法を検討すること。
- リクエストスコープのキー名 `errors` はコンポーネント設定ファイルの `WebConfig.errorMessageRequestAttributeName` で変更可能。

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
- OnErrorインターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md
  OnErrorを使用する
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  ウェブアプリケーションのユーザ入力値のチェックを行う
  バリデーションエラー時のエラーメッセージを定義する