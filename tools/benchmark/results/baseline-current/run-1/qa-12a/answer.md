**結論**: 入力チェック（バリデーション）でエラーが発生した場合、Nablarch 6ではHTTPエラー制御ハンドラが自動的にエラーメッセージをリクエストスコープ（デフォルトキー名: `errors`）に格納し、テンプレートエンジン側でそのオブジェクトにアクセスして表示します。

**根拠**:

### 全体的な仕組み

バリデーションエラーが発生すると、以下の流れでエラーメッセージがユーザーに返されます。

1. アクションハンドラでバリデーションエラーが発生 → `HttpErrorResponse`（原因例外: `ApplicationException`）が送出される
2. **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）が `ApplicationException` の保持するメッセージ情報を `ErrorMessages` に変換し、リクエストスコープに設定する（デフォルトキー名: `errors`）
3. テンプレートエンジン（Thymeleaf等）がリクエストスコープの `ErrorMessages` にアクセスしてエラーメッセージを表示する

### ウェブアプリケーションでのバリデーション実行

ウェブアプリケーションのユーザ入力値のチェックは **InjectFormインターセプタ** を使用します。Bean Validationを使う場合は、コンポーネント設定ファイルに以下を定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### エラーメッセージの定義

バリデーションアノテーションのメッセージは、メッセージ管理機能（.propertiesファイル）で定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

### 画面でのエラーメッセージ表示（Thymeleafの例）

特定のプロパティに対応したメッセージを表示したい場合:

```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのメッセージを表示したい場合:

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージを表示したい場合:

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

### アクションで任意のプロパティにエラーメッセージを設定したい場合

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

### エラーメッセージに項目名を含めたい場合

```xml
<component name="constraintViolationConverterFactory"
    class="nablarch.core.validation.ee.ItemNamedConstraintViolationConverterFactory" />
```

**注意点**:
- リクエストスコープのキー名はデフォルトで `errors`。変更する場合はコンポーネント設定ファイルの `WebConfig#errorMessageRequestAttributeName` プロパティで設定する
- JSPでカスタムタグを使用するとDOM構造の制約によりCSSフレームワークとの相性が悪い場合がある。リクエストスコープの `ErrorMessages` オブジェクトに直接アクセスする方が柔軟
- `BeanValidationStrategy` のエラーメッセージのソート順はアプリケーションサーバの `getParameterNames` 実装依存であるため、固定順が必要な場合は `BeanValidationStrategy` を継承してカスタマイズする

参照: processing-pattern/web-application/web-application-error-message.json, component/libraries/libraries-bean-validation.json#s7, component/libraries/libraries-bean-validation.json#s16, component/libraries/libraries-bean-validation.json#s13, component/handlers/handlers-HttpErrorHandler.json#s4, component/libraries/libraries-bean-validation.json#s19