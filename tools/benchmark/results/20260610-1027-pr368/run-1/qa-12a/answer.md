**結論**: ウェブアプリケーションでバリデーションエラーのメッセージをユーザーに返すには、アクションに `@InjectForm` + `@OnError` アノテーションを付け、ビューでリクエストスコープの `errors` オブジェクト（`ErrorMessages`）からメッセージを取得して表示します。

**根拠**:

#### 1. バリデーション設定（コンポーネント定義ファイル）

Bean Validation を使う場合、`BeanValidationStrategy` をコンポーネント定義に追加します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### 2. アクション側の実装

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先を指定します。`@OnError` を付けないとバリデーションエラーがシステムエラー扱いになるため必須です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う。
}
```

バリデーションエラー発生時、`HTTPエラー制御ハンドラ` が `ApplicationException` の保持するメッセージを `ErrorMessages` に変換し、リクエストスコープのキー `errors` に格納します。

#### 3. エラーメッセージの定義

プロパティファイルにメッセージIDをキーとして定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

#### 4. ビュー側の表示（Thymeleaf の例）

リクエストスコープの `errors` オブジェクトを使ってメッセージを表示します。

**特定の項目のエラーを表示**:
```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**グローバルメッセージ（項目に紐付かない）を表示**:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**全エラーメッセージを表示**:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

JSP を使う場合は、カスタムタグ（`<n:errors>` など）か、リクエストスコープに直接アクセスしてメッセージを表示できます（カスタムタグはCSSフレームワークとの相性に課題あり）。

**注意点**:
- `@OnError` を付けない場合、バリデーションエラーがシステムエラー扱いとなります。必ず設定してください。
- リクエストスコープのキー名はデフォルト `errors` ですが、コンポーネント設定ファイルで `errorMessageRequestAttributeName` を変更できます。
- エラー遷移先でプルダウン選択肢などの表示データが必要な場合は、`@OnError(path = "forward://initializeRegisterPage")` のように内部フォワードを使用して表示データを取得します。

参照: web-application-error-message.json:s0 / handlers-InjectForm.json:s3 / handlers-InjectForm.json:s4 / handlers-on-error.json:s3 / handlers-HttpErrorHandler.json:s4 / libraries-bean-validation.json:s7 / libraries-bean-validation.json:s16