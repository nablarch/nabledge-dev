**結論**: RESTfulウェブサービスで入力チェックエラーのメッセージをクライアントに返すには、(1) リソースメソッドに `@Valid` アノテーションを付与してバリデーションを実行し、(2) `ErrorResponseBuilder` を継承してバリデーションエラー時にメッセージ入りのレスポンスボディを構築する実装を追加する。

---

**根拠**:

**① リソースメソッドに `@Valid` を付与してバリデーションを実行する**

`JaxRsBeanValidationHandler` が処理するため、バリデーション対象メソッドに `@Valid` を付与するだけでよい。エラー発生時は `ApplicationException` がスローされる。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

`JaxRsBeanValidationHandler` は `JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）よりも後段に配置する必要がある。

**② `ErrorResponseBuilder` を継承してエラーメッセージをレスポンスに含める**

デフォルトの `ErrorResponseBuilder` はエラーメッセージをレスポンスボディに含めない。バリデーションエラー時（`ApplicationException`）にメッセージを返したい場合は、以下のように継承クラスを作成する。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public HttpResponse build(final HttpRequest request,
            final ExecutionContext context, final Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        } else {
            return super.build(request, context, throwable);
        }
    }

    private HttpResponse createResponseBody(final ApplicationException ae) {
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);

        // エラーメッセージの生成処理は省略

        try {
            response.write(objectMapper.writeValueAsString(errorMessages));
        } catch (JsonProcessingException ignored) {
            return new HttpResponse(500);
        }
        return response;
    }
}
```

コンポーネント設定ファイルに登録する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージはプロパティファイルに定義する**

Bean Validationのアノテーションに対応するメッセージIDをキーにプロパティファイルへ定義する。

```properties
# Lengthアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。

# Requiredアノテーションのメッセージ
nablarch.core.validation.ee.Required.message=必須項目です。
```

---

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生するとレスポンスが返せなくなるため、継承クラスの実装では例外が発生しないよう注意すること。
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）より後段に設定すること（変換済みのFormに対してバリデーションを行うため）。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17