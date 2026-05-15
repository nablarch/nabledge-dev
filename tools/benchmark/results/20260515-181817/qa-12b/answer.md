**結論**: 入力チェック（バリデーション）でエラーが発生した場合、`ApplicationException` をスローすると、HTTPエラー制御ハンドラが自動的にエラーメッセージを `ErrorMessages` に変換してリクエストスコープ（デフォルトキー名: `errors`）に格納します。テンプレート（Thymeleaf等）ではこの `errors` オブジェクトを参照してエラーメッセージを表示します。

**根拠**:

### 1. エラーメッセージのリクエストスコープへの格納（自動）

バリデーションエラー時は `ApplicationException` を送出するだけでOKです。HTTPエラー制御ハンドラ（`HttpErrorHandler`）が `ApplicationException` を保持する `HttpErrorResponse` を受け取ると、保持するメッセージ情報を `ErrorMessages` に変換してリクエストスコープに自動的に設定します。

デフォルトのキー名は `errors`（`WebConfig#errorMessageRequestAttributeName` で変更可）。

```xml
<!-- キー名をmessagesに変更したい場合 -->
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 2. ApplicationException のスロー方法

**業務ロジック内でエラーを生成したい場合**（DB相関バリデーション等）:

```java
// 特定の項目に紐づくエラー
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));

// 汎用的な業務例外
Message message = MessageUtil.createMessage(MessageLevel.ERROR, "errors.login.alreadyExist");
throw new ApplicationException(message);
```

`messages.properties` にメッセージを定義:

```properties
duplicate.mailAddress=このメールアドレスは既に使用されています。
errors.login.alreadyExist=入力されたログインIDは既に登録されています。別のログインIDを入力してください。
```

### 3. テンプレートでのエラーメッセージ表示（Thymeleaf）

```html
<!-- 特定の項目のエラーを表示 -->
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- プロパティに紐付かないグローバルメッセージを表示 -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>

<!-- 全メッセージを一括表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 4. Bean Validation でのメッセージ定義

```java
public class SampleForm {
  @Required
  @Length(max = 10)
  private String userName;
}
```

```properties
# messages.properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `errors` キー名はデフォルト値であり、`WebConfig#errorMessageRequestAttributeName` で変更可能です。テンプレート側のキー名もそれに合わせて変更する必要があります。
- `ValidationUtil#createMessageForProperty` を使う場合、第1引数のプロパティ名は画面側のフィールド名（`form.mailAddress` 等）と一致させる必要があります。
- Bean Validationのメッセージは `{` `}` で囲まれた場合のみメッセージ管理が使用されます。EL式は使用不可です。

参照: processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-HttpErrorHandler.json#s4, component/libraries/libraries-bean-validation.json#s7, component/libraries/libraries-bean-validation.json#s13, component/libraries/libraries-message.json#s9