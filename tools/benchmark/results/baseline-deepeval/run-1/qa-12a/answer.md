十分な情報が収集できました。回答を生成します。

## Step 5-7: 回答生成・検証

収集したセクション情報に基づいて回答を生成します。

---

**結論**: ウェブアプリケーションで入力チェックエラーをユーザーに返すには、`@InjectForm` と `@OnError` アノテーションを組み合わせてバリデーションを実行し、JSPでは `<n:error>` / `<n:errors>` カスタムタグ、Thymeleafでは `ErrorMessages` オブジェクト経由でエラーメッセージを表示します。

**根拠**:

### 1. アクションクラスの実装

`@InjectForm` アノテーションでバリデーションを実行し、`@OnError` でエラー時の遷移先を指定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション成功時のみここに到達する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う。
}
```

- `prefix = "form"` により、`form.xxx` という名前のリクエストパラメータがバリデーション対象になります
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いになるため**必ず設定**してください

### 2. エラーメッセージの仕組み

バリデーションエラー発生時、`HTTPエラー制御ハンドラ`が以下の処理を自動で行います：

1. `ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換する
2. `ErrorMessages` をリクエストスコープのキー `errors` に設定する（キー名はコンポーネント設定で変更可能）

### 3. JSP（カスタムタグ）でのエラー表示

**項目ごとにエラーメッセージを表示する場合**（`<n:error>` タグ）:

```jsp
<div>
  <label>ユーザーID</label>
  <n:text name="form.userId" />
  <!-- 入力項目と同じ名前をname属性に指定する -->
  <n:error name="form.userId" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

**全エラーメッセージを一覧表示する場合**（`<n:errors>` タグ）:

```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

### 4. Thymeleafでのエラー表示

リクエストスコープの `errors`（`ErrorMessages` オブジェクト）を直接使用します：

```html
<!-- 特定プロパティのエラーメッセージを表示する -->
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全メッセージを表示する -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 5. エラーメッセージの定義

`@Required` などのアノテーションに対応するエラーメッセージは、プロパティファイルで定義します：

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `@OnError` を設定しないと、バリデーションエラーが500エラーになります
- Formクラスのプロパティは**必ず `String` 型**にしてください（型変換の例外を防ぐため）
- Bean Validationを使う場合、コンポーネント設定ファイルに `BeanValidationStrategy` を `validationStrategy` という名前で定義する必要があります

参照: `processing-pattern/web-application/web-application-error-message.json`, `component/handlers/handlers-InjectForm.json:s3`, `component/handlers/handlers-InjectForm.json:s4`, `component/handlers/handlers-HttpErrorHandler.json:s4`, `component/libraries/libraries-bean-validation.json:s7`, `component/libraries/libraries-bean-validation.json:s16`, `component/libraries/libraries-tag.json:s29`

---