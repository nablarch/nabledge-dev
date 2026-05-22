Step 5-7: 回答生成と検証を行います。

---

**結論**: `@InjectForm` + `@OnError` アノテーションの組み合わせで入力チェックを実行し、エラー発生時にフォームページへフォワードする。画面側では Nablarch カスタムタグ `<n:errors>` / `<n:error>` でエラーメッセージを表示する。

**根拠**:

**① アクション側の実装**

`@InjectForm` でバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。`@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

**② Bean Validation の設定**

コンポーネント設定ファイルに `BeanValidationStrategy` を定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**③ エラーメッセージの定義**

`classpath:messages.properties`（UTF-8）にメッセージIDとテキストを定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須入力です。
errors.login.alreadyExist=入力されたログインIDは既に登録されています。
```

Bean Validation アノテーションの `message` 属性には、`{メッセージID}` 形式でメッセージIDを指定する。

**④ 画面側のエラー表示（JSP）**

全エラーを一覧表示する場合は `<n:errors>`、項目ごとに個別表示する場合は `<n:error>` を使用する。エラーがあった入力項目は自動的に `nablarch_error` CSS クラスが付与されハイライト表示される。

```jsp
<!-- 全エラーを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 項目ごとの個別表示 -->
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**⑤ アクション内で業務エラーを返す場合**

データベース重複チェックなど業務ロジック内でエラーを返す場合は `ApplicationException` を送出する。

```java
// 特定項目に紐づけたい場合
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));

// グローバルエラー（項目に紐づかない）の場合
Message message = MessageUtil.createMessage(MessageLevel.ERROR, "errors.login.alreadyExist");
throw new ApplicationException(message);
```

グローバルエラーは `<n:errors filter="global">` で表示する。

**注意点**:
- `@OnError` が未設定だとバリデーションエラーがシステムエラー扱いになる
- `BeanValidationStrategy` のエラーメッセージのソート順はアプリケーションサーバ実装依存であり、順序を保証したい場合はサブクラス化して対応する

参照: `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `handlers-on-error.json:s3`, `libraries-bean-validation.json:s16`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s13`, `libraries-tag.json:s29`, `libraries-message.json:s7`, `libraries-message.json:s9`

---