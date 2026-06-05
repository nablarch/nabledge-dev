セクション内容を確認しました。Step 5で回答を生成します。

---

**結論**: `@InjectForm`でバリデーションを実行し、`@OnError`でエラー時の遷移先を指定する。エラーメッセージは `HTTPエラー制御ハンドラ` がリクエストスコープの `errors` キーに `ErrorMessages` として格納するので、テンプレート（Thymeleaf/JSP）からそれを参照して表示する。

**根拠**:

### 1. アクションクラスの実装

```java
@InjectForm(form = UserForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://initializeRegisterPage")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // バリデーション通過後の業務処理
}
```

- `@InjectForm` がリクエストパラメータに対してバリデーションを実行する
- `@OnError` を必ず設定すること。設定しない場合はバリデーションエラーがシステムエラー扱いになる
- `path = "forward://..."` で内部フォワードし、プルダウン選択肢などの表示データを取得させることもできる

### 2. コンポーネント設定（Bean Validationを使用する場合）

```xml
<component name="validationStrategy"
    class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 3. Thymeleafでのエラーメッセージ表示

`HTTPエラー制御ハンドラ`が `ApplicationException` のメッセージを `ErrorMessages` に変換し、リクエストスコープの `errors` キーに設定する。

```html
<!-- 特定プロパティのエラーを表示 -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全てのエラーを一覧表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 4. JSP（Nablarchカスタムタグ）でのエラー表示

```jsp
<n:form>
  <n:text name="form.userId" />
  <n:error name="form.userId" messageFormat="span" errorCss="alert alert-danger" />
</n:form>
```

**注意点**:
- `@OnError` は `@InjectForm` と同じメソッドに必ず設定すること（未設定だとシステムエラー扱い）
- JSPのカスタムタグ（`<n:error>`）はCSSフレームワークとの相性が悪い場合がある。その場合はリクエストスコープの `errors` オブジェクトに直接アクセスする方法を検討すること
- `errors` キー名はコンポーネント設定の `WebConfig#errorMessageRequestAttributeName` で変更可能

参照: handlers-HttpErrorHandler.json:s4, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-on-error.json:s3, handlers-on-error.json:s4, processing-pattern/web-application/web-application-error-message.json, libraries-bean-validation.json:s16, libraries-tag.json:s8

---