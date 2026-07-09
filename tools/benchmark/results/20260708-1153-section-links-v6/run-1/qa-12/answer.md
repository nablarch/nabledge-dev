**結論**: `@InjectForm` + `@OnError` アノテーションで入力チェックとエラー時の遷移先を設定し、テンプレート（Thymeleaf/JSP）でリクエストスコープの `ErrorMessages` オブジェクトを参照してエラーメッセージを表示する。

---

**根拠**:

**① バリデーションの実行（業務アクション側）**

`@InjectForm` アノテーションを業務アクションのメソッドに設定する。`@OnError` を必ず一緒に設定すること（設定しないとバリデーションエラーがシステムエラー扱いになる）。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション済みのフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う
}
```

**② エラーメッセージがリクエストスコープに格納される仕組み**

HTTPエラー制御ハンドラが `ApplicationException` を受け取り、`ErrorMessages` に変換してリクエストスコープに設定する。リクエストスコープのキー名はデフォルトで `errors`。

キー名を変更したい場合は以下のように設定する：

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーをmessagesに変更 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

**③ テンプレート側でのエラーメッセージ表示（Thymeleaf例）**

特定プロパティのエラーメッセージを表示：

```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのメッセージを表示：

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（プロパティに紐付かないメッセージ）を表示：

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**④ コンポーネント設定（Bean Validation使用時）**

`@InjectForm` でBean Validationを使うには、コンポーネント設定ファイルに以下を追加：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**⑤ バリデーションエラー時のメッセージ定義**

プロパティファイルにアノテーションのメッセージIDをキーとして定義する：

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:
- `@OnError` を設定しないと `ApplicationException` がシステムエラーとして扱われる
- JSPを使用する場合はNablarchカスタムタグ（`<n:errors>` タグ）でも表示できるが、DOM構造の制約によりCSSフレームワークとの相性が悪い場合があるため、リクエストスコープの `ErrorMessages` オブジェクトを直接使用する方法も選択肢になる

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
  ウェブアプリケーションのユーザ入力値のチェックを行う
  バリデーションエラー時のエラーメッセージを定義する