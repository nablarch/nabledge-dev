**結論**: ウェブアプリケーションでバリデーションエラーのメッセージをユーザーに返すには、業務アクションに `@InjectForm` と `@OnError` アノテーションを設定し、`HTTPエラー制御ハンドラ` がリクエストスコープに格納した `ErrorMessages` オブジェクトをテンプレートエンジンで参照して表示します。

**根拠**:

**1. 業務アクションの実装**

`@InjectForm` でフォームのバリデーションを実行し、`@OnError` でバリデーションエラー発生時の遷移先を指定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション済みのフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う
}
```

> `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必須です。

**2. エラーメッセージのリクエストスコープへの格納**

`HTTPエラー制御ハンドラ` が `ApplicationException` を受け取ると、保持するメッセージ情報を `ErrorMessages` に変換し、デフォルトキー名 `errors` でリクエストスコープに格納します。

**3. テンプレート（Thymeleaf）でのエラーメッセージ表示**

特定のプロパティのエラーを表示する場合:
```html
<input type='text' name='form.userName' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全てのエラーメッセージを表示する場合:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

グローバルメッセージ（特定プロパティに紐づかないメッセージ）を表示する場合:
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

**注意点**:
- リクエストスコープのキー名は `errors` がデフォルトですが、`WebConfig` の `errorMessageRequestAttributeName` プロパティで変更できます。
- エラー時の遷移先画面でプルダウン選択肢などの表示データが必要な場合は、`@OnError` の `path` 属性に内部フォワード（`forward://`）を使って初期表示メソッドに処理を委譲します。
- JSPを使う場合はカスタムタグの `<n:errors>` も使えますが、DOM構造の制約でCSSフレームワークと相性が悪い問題があります。リクエストスコープ上のオブジェクトに直接アクセスする方法も選択できます。

参照: web-application-error-message.json, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-on-error.json:s3, handlers-HttpErrorHandler.json:s4