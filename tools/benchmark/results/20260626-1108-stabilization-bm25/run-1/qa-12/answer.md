**結論**: ウェブアプリケーションでは、`@InjectForm` + `@OnError` アノテーションでバリデーションエラー時の遷移先を指定し、JSP側で `<n:error>` カスタムタグを使ってエラーメッセージを表示します。エラーメッセージ本文は `messages.properties` に定義します。

---

**根拠**:

**① メッセージをプロパティファイルに定義する**

`messages.properties` にメッセージIDとメッセージ文字列を定義します。

```properties
# Bean Validationアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必ず入力してください。

# 業務ロジック内で使用するメッセージ
errors.login.alreadyExist=入力されたログインIDは既に登録されています。別のログインIDを入力してください。
```

**② コンポーネント設定ファイルに BeanValidationStrategy を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**③ アクションに @InjectForm と @OnError を設定する**

`@OnError` でバリデーションエラー時の遷移先を指定しないと、エラーがシステムエラー扱いになるため必須です。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション成功後の処理
    UserForm form = ctx.getRequestScopedVar("form");
    // ...
}
```

**④ JSP で `<n:error>` タグを使ってエラーメッセージを表示する**

バリデーションエラーがあると `@OnError` で指定した画面に遷移し、`<n:error>` タグがエラーメッセージを表示します。

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>

<n:form>
  <div>
    <label>ユーザID</label>
    <n:text name="form.userId" />
    <n:error name="form.userId" messageFormat="span" errorCss="alert alert-danger" />
  </div>
  <div>
    <label>パスワード</label>
    <n:password name="form.password" />
    <n:error name="form.password" messageFormat="span" errorCss="alert alert-danger" />
  </div>
  <n:submit type="submit" uri="/action/register" value="登録" />
</n:form>
```

**⑤ 業務ロジック内でエラーを返したい場合（特定項目への紐付け）**

アクション内でデータベースとの相関チェックなど手動でエラーを発生させる場合は、`ValidationUtil.createMessageForProperty` と `ApplicationException` を使います。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

メッセージIDのみで特定項目に紐付けない場合は `MessageUtil` を使います。

```java
Message message = MessageUtil.createMessage(MessageLevel.ERROR, "errors.login.alreadyExist");
throw new ApplicationException(message);
```

---

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、必ず設定すること
- `BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義することが必須
- `<n:error>` の `name` 属性には、対応する入力項目の `name` 属性と同じ値（例: `form.userId`）を指定する

参照:
- `libraries-bean-validation.json:s7`
- `libraries-bean-validation.json:s16`
- `handlers-InjectForm.json:s3`
- `handlers-InjectForm.json:s4`
- `libraries-tag.json:s8`
- `libraries-bean-validation.json:s13`
- `libraries-message.json:s7`
- `libraries-message.json:s9`