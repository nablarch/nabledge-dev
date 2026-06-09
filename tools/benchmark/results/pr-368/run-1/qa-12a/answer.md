**結論**: ウェブアプリケーションで入力チェックエラーをユーザーに返すには、`@InjectForm` + `@OnError` でエラー時の遷移先を指定し、Viewから `ErrorMessages` オブジェクト（リクエストスコープの `errors`）にアクセスしてメッセージを表示します。

**根拠**:

**1. アクション側の実装**

`@InjectForm` アノテーションで入力値チェックを実行し、`@OnError` でバリデーションエラー時の遷移先を指定します。`@OnError` を設定しない場合はバリデーションエラーがシステムエラー扱いになるため必須です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション成功時のみここに到達する
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

**2. エラーメッセージの自動格納（フレームワークの動作）**

バリデーションエラー（`ApplicationException`）が発生すると、`HTTPエラー制御ハンドラ` が自動的に以下を行います：
1. `ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換する
2. `ErrorMessages` をリクエストスコープにキー名 `errors` で設定する

アプリケーション側でこの変換を実装する必要はありません。

**3. Viewでのエラーメッセージ表示（Thymeleafの場合）**

特定のプロパティに対応したメッセージを表示：
```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのメッセージをまとめて表示：
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（特定プロパティに紐付かないメッセージ）を表示：
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**4. Bean Validation のコンポーネント設定**

`@InjectForm` で Bean Validation を使用するには、コンポーネント設定ファイルに以下を追加する必要があります：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**5. エラーメッセージの定義**

バリデーションアノテーションのデフォルトメッセージIDに対してプロパティファイルでメッセージを定義します：

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、必ず設定すること
- リクエストスコープのキー名はデフォルトで `errors`。変更する場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定する
- JSPを使う場合は `<n:errors>` カスタムタグでも表示できるが、DOM構造の制約があるためCSSフレームワークとの相性に注意

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, handlers-on-error.json:s3, libraries-bean-validation.json:s7, libraries-bean-validation.json:s16