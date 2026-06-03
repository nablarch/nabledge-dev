これで必要な情報が揃いました。Step 5に進んで回答を生成します。

**read_sections:**
- `processing-pattern/web-application/web-application-error-message.json:s1`
- `component/handlers/handlers-InjectForm.json:s3`
- `component/handlers/handlers-InjectForm.json:s4`
- `component/handlers/handlers-HttpErrorHandler.json:s4`
- `component/libraries/libraries-bean-validation.json:s7`
- `component/libraries/libraries-bean-validation.json:s16`

---

## Step 5: 回答生成

**結論**: ウェブアプリケーションでバリデーションエラーメッセージをユーザーに返すには、アクションメソッドに `@InjectForm` と `@OnError` アノテーションを設定し、`HTTPエラー制御ハンドラ`がリクエストスコープに格納する `ErrorMessages`（変数名: `errors`）をテンプレート（Thymeleaf/JSP）で参照して表示します。

---

**根拠**:

### 1. アクション側の実装

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先（入力画面）を指定します。`@OnError` を付けないとバリデーションエラーがシステムエラー扱いになるため、必ず設定してください。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理を行う
}
```

Bean Validation を使う場合は、コンポーネント設定ファイルに以下を追加します。

```xml
<component name="validationStrategy"
           class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. エラーメッセージの仕組み

バリデーションエラー発生時、`HTTPエラー制御ハンドラ`が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー `errors`（デフォルト）に格納します。

キー名を変更したい場合は以下のように設定できます。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
    <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 3. テンプレート側でのエラー表示（Thymeleaf の場合）

**特定の入力項目に対するエラー:**

```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**全てのエラーメッセージを一覧表示:**

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**グローバルメッセージ（項目に紐付かないメッセージ）:**

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

### 4. エラーメッセージの定義

Bean Validation のアノテーションに対するエラーメッセージはプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:

- `@OnError` を業務アクションに付けないと、バリデーションエラーがシステムエラー（500）として扱われます。
- JSP を使う場合はカスタムタグ（`<n:errors>`）でもエラー表示できますが、CSSフレームワークとの相性問題があるため、リクエストスコープ上の `ErrorMessages` に直接アクセスする方法も選択肢です。

参照: `web-application-error-message.json:s1`、`handlers-InjectForm.json:s3`、`handlers-InjectForm.json:s4`、`handlers-HttpErrorHandler.json:s4`、`libraries-bean-validation.json:s7`、`libraries-bean-validation.json:s16`

---

## Step 6: verify

**抽出するNablarch固有クレーム:**

1. "`@InjectForm`アノテーションでバリデーションを実行し、フォームオブジェクトをリクエストスコープに格納する"
   → s3に明示。✅

2. "`@OnError`でエラー時の遷移先を指定する。設定しないとバリデーションエラーがシステムエラー扱いになる"
   → s4に「OnErrorが設定されていない場合、バリデーションエラーがシステムエラー扱いとなる」と明示。✅

3. "`HTTPエラー制御ハンドラ`が`ApplicationException`のメッセージを`ErrorMessages`に変換してリクエストスコープのキー`errors`に格納する"
   → s4に明示。✅

4. "`BeanValidationStrategy`を`validationStrategy`という名前でコンポーネント定義する"
   → s16に明示。✅

5. "`ErrorMessages#hasError`/`getMessage`/`getGlobalMessages`/`getAllMessages`でメッセージを参照できる"
   → s1に全て明示。✅

6. "エラーメッセージはプロパティファイルで`{max}`などのプレースホルダを使い定義できる"
   → s7に明示。✅

7. "`errorMessageRequestAttributeName`でリクエストスコープのキー名を変更できる"
   → s4に明示。✅

**verify_result = PASS**

---

## Step 8: 最終回答

**結論**: ウェブアプリケーションでバリデーションエラーメッセージをユーザーに返すには、アクションメソッドに `@InjectForm` と `@OnError` を設定し、`HTTPエラー制御ハンドラ`がリクエストスコープに格納した `ErrorMessages`（変数名: `errors`）をテンプレートで参照して表示します。

---

**根拠**:

### 1. アクション実装

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先（入力画面）を指定します。**`@OnError` を付けないとバリデーションエラーがシステムエラー扱いになる**ため必須です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

Bean Validation を使う場合はコンポーネント設定も必要です。

```xml
<component name="validationStrategy"
           class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. エラーメッセージの仕組み

バリデーションエラー発生時、`HTTPエラー制御ハンドラ`が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー **`errors`**（デフォルト）に格納します。

キー名を変更したい場合:

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
    <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 3. テンプレートでのエラー表示（Thymeleaf の場合）

**特定項目のエラー:**

```html
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**全エラーメッセージを一覧表示:**

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**グローバルメッセージ（項目に紐付かないメッセージ）:**

```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

### 4. エラーメッセージの定義

Bean Validation アノテーションのエラーメッセージはプロパティファイルで定義します。プレースホルダでアノテーション属性値を埋め込めます。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:

- `@OnError` を省略するとバリデーションエラーがシステムエラー（500）扱いになります。
- JSP の場合はカスタムタグ（`<n:errors>`）でも表示できますが、CSSフレームワークとの相性問題があるため、`${errors}` でリクエストスコープに直接アクセスする方法も選択肢です。

参照: `web-application-error-message.json:s1`、`handlers-InjectForm.json:s3`、`handlers-InjectForm.json:s4`、`handlers-HttpErrorHandler.json:s4`、`libraries-bean-validation.json:s7`、`libraries-bean-validation.json:s16`

---