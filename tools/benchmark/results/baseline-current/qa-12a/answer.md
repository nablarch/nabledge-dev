**結論**: ウェブアプリケーションでバリデーションエラーメッセージをユーザーに返すには、`@InjectForm` + `@OnError` でエラー遷移先を設定し、テンプレート側でリクエストスコープの `errors` オブジェクト（`ErrorMessages`）にアクセスしてメッセージを表示します。

**根拠**:

### 1. アクション側の実装

`@InjectForm` アノテーションでバリデーション対象フォームを指定し、`@OnError` でエラー時の遷移先を設定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション成功時のみここに到達
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。

### 2. エラーメッセージの伝達の仕組み

バリデーションエラー発生時、`HttpErrorHandler`（HTTPエラー制御ハンドラ）が以下の処理を自動的に行います。

1. `ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換する
2. `ErrorMessages` をリクエストスコープのキー `errors` に設定する（キー名はデフォルト値）

キー名を変更したい場合は以下の設定を行います。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーをmessagesに変更 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 3. テンプレート側でのエラー表示（Thymeleafの例）

**特定のプロパティに対応したメッセージを表示したい場合**

```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**グローバルメッセージ（プロパティに紐付かないメッセージ）を表示したい場合**

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**全てのメッセージを表示したい場合**

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 4. メッセージの定義

バリデーションエラーメッセージは、バリデーションアノテーションのデフォルトメッセージIDをキーにプロパティファイルに定義します。

```properties
# Lengthアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。

# SystemCharに対応したメッセージ
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

### 5. Bean Validationを使う場合の追加設定

`@InjectForm` でBean Validationを使用するには、コンポーネント設定ファイルに以下を追加します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- JSPを使用している場合、カスタムタグ（`n:errors` 等）でも表示可能ですが、カスタムタグが出力するDOM構造の制約によりCSSフレームワークとの相性が悪い問題があります。リクエストスコープ上の `ErrorMessages` に直接アクセスする方法の方が柔軟です。
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー（500）として扱われてしまうため注意してください。
- `BeanValidationStrategy` のエラーメッセージのソート順は `jakarta.servlet.ServletRequest#getParameterNames` が返す順序に依存しており、アプリケーションサーバによって変わる可能性があります。

参照:
- `processing-pattern/web-application/web-application-error-message.json`
- `component/handlers/handlers-HttpErrorHandler.json#s4`
- `component/handlers/handlers-InjectForm.json#s3`
- `component/handlers/handlers-InjectForm.json#s4`
- `component/libraries/libraries-bean-validation.json#s7`
- `component/libraries/libraries-bean-validation.json#s16`