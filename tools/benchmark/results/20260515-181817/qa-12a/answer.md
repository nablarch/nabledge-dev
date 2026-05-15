**結論**: バリデーションエラー時のメッセージ返却方法は、アプリケーション種別（Webアプリ／RESTサービス）とバリデーションの実施場所によって異なります。

### 1. Webアプリケーション（画面系）

#### (1) Bean Validation によるバリデーションエラー → 画面遷移

業務アクションに `@InjectForm` と `@OnError` を設定します。バリデーションエラーが発生すると、`@OnError` で指定したJSPに自動で遷移し、エラーメッセージが表示されます。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

注意: `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになります。

コンポーネント設定ファイルに以下の定義が必要です。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### (2) アクションハンドラ内でエラーを明示的に発生させる（相関チェック等）

`ValidationUtil#createMessageForProperty` でエラーメッセージを構築し、`ApplicationException` をスローします。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

### 2. RESTful Webサービス

#### (1) `@Valid` によるバリデーション

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

#### (2) エラーレスポンスにメッセージを設定する

`ErrorResponseBuilder` を継承してJSONエラーレスポンスを構築します。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    private final ObjectMapper objectMapper = new ObjectMapper();

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
        try {
            response.write(objectMapper.writeValueAsString(errorMessages));
        } catch (JsonProcessingException ignored) {
            return new HttpResponse(500);
        }
        return response;
    }
}
```

### 3. エラーメッセージの定義方法

メッセージはpropertiesファイルで定義します。アノテーションの属性値をプレースホルダとして埋め込めます。

```properties
nablarch.core.validation.ee.Length.min.message={min}文字以上で入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

メッセージに項目名を含めたい場合は `ItemNamedConstraintViolationConverterFactory` を使うと `[項目名]メッセージ` の形式で出力できます。

```xml
<component name="constraintViolationConverterFactory"
    class="nablarch.core.validation.ee.ItemNamedConstraintViolationConverterFactory" />
```

**注意点**:
- Webアプリで `@OnError` を設定し忘れると、`ApplicationException` がシステムエラーとして扱われます。
- `BeanValidationStrategy` のエラーメッセージのソート順はアプリケーションサーバ依存になる場合があります（カスタマイズ可能）。
- RESTサービスでは `ErrorResponseBuilder` の継承クラスをコンポーネント設定に登録する必要があります。

参照:
- component/handlers/handlers-InjectForm.json#s3
- component/handlers/handlers-InjectForm.json#s4
- component/libraries/libraries-bean-validation.json#s7
- component/libraries/libraries-bean-validation.json#s13
- component/libraries/libraries-bean-validation.json#s16
- component/libraries/libraries-bean-validation.json#s19
- component/handlers/handlers-jaxrs-response-handler.json#s7
- component/handlers/handlers-jaxrs-bean-validation-handler.json#s4