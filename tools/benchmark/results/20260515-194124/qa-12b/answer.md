**結論**: 入力チェックエラー時のエラーメッセージ返却方法は、アプリケーション種別（ウェブ / RESTful）によって異なります。

## ウェブアプリケーションの場合

**`@InjectForm` + `@OnError` アノテーションを使用する**

バリデーションエラーが発生すると `ApplicationException` がスローされます。`@OnError` でエラー時の遷移先画面を指定することで、エラーメッセージが画面に返却されます。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

> **注意**: `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになります。必ず設定してください。

## エラーメッセージの定義

デフォルトでは **メッセージ管理** を通じてエラーメッセージを構築します。アノテーションの `message` 属性のメッセージIDに対応するメッセージをプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

## 特定項目に紐づくエラーメッセージを手動で発行する場合

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

## RESTful ウェブサービスの場合

**`@Valid` アノテーション + `ErrorResponseBuilder` を使用する**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

エラーレスポンスのボディにメッセージを含めたい場合は、`ErrorResponseBuilder` を継承してカスタム実装します。

**注意点**:
- ウェブアプリでBean Validationを使うには、コンポーネント設定に `BeanValidationStrategy` を `validationStrategy` という名前で定義する必要があります。
- `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになります。
- バリデーションエラー時に任意処理を行いたい場合は、明示的に `try-catch ApplicationException` でハンドリングしてから再スローします。

参照: `component/handlers/handlers-InjectForm.json#s3`, `component/handlers/handlers-InjectForm.json#s4`, `component/handlers/handlers-on-error.json#s3`, `component/libraries/libraries-bean-validation.json#s7`, `component/libraries/libraries-bean-validation.json#s13`, `component/handlers/handlers-jaxrs-response-handler.json#s7`