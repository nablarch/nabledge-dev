**結論**: 入力チェックエラー時のユーザーへのメッセージ返却方法は、処理方式（ウェブ/REST）によって異なります。

## ウェブアプリケーションの場合

`@InjectForm` + `@OnError` アノテーションの組み合わせを使用します。バリデーションエラー発生時に `ApplicationException` が送出され、`@OnError` で指定した画面へ遷移します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること。

## RESTful ウェブサービスの場合

エラーレスポンスのボディにメッセージを含めるには `ErrorResponseBuilder` を継承してカスタマイズします。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        } else {
            return super.build(request, context, throwable);
        }
    }

    private HttpResponse createResponseBody(ApplicationException ae) {
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        // エラーメッセージの生成処理...
        return response;
    }
}
```

## エラーメッセージの定義方法

デフォルトでは `NablarchMessageInterpolator` がメッセージ管理を使用します。プロパティファイルにアノテーションのメッセージIDをキーにして定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

## 特定項目に紐づくエラーメッセージ（アクション内でバリデーションする場合）

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

## メッセージに項目名を含めたい場合

```xml
<component name="constraintViolationConverterFactory"
    class="nablarch.core.validation.ee.ItemNamedConstraintViolationConverterFactory" />
```

```properties
sample.User.name = ユーザ名
sample.User.address = 住所
```

生成されるメッセージ例: `[ユーザ名]入力してください。`

**注意点**:
- フォームクラスのプロパティは必ず `String` 型で定義すること
- `@OnError` なしで `@InjectForm` を使用するとバリデーションエラーがシステムエラー扱いになる
- `ErrorResponseBuilder` 内で例外が発生するとレスポンスが生成されなくなるため、例外が発生しないよう実装すること

参照: `libraries-bean-validation.json#s7`, `libraries-bean-validation.json#s13`, `libraries-bean-validation.json#s19`, `handlers-InjectForm.json#s4`, `handlers-jaxrs-response-handler.json#s7`