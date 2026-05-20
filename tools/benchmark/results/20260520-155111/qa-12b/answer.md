**結論**: RESTfulウェブサービスでは、リソースクラスのメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、エラーメッセージをレスポンスに含めたい場合は `ErrorResponseBuilder` をカスタマイズして `ApplicationException` を処理します。

**根拠**:

**1. バリデーションの設定（`@Valid` アノテーション）**

リソースクラスのメソッドに `@Valid` を設定することで、`JaxRsBeanValidationHandler` がForm(Bean)に対してBean Validationを実行します。エラーが発生した場合は `ApplicationException` が送出されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**2. エラーメッセージをレスポンスボディに設定する**

`JaxRsResponseHandler` の `ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` をキャッチしてエラーメッセージを含むレスポンス（例: JSON形式）を構築します。

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

コンポーネント設定ファイルに登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せない状態になります。カスタマイズ時は処理中に例外が発生しないよう実装してください。
- バリデーションエラーメッセージの内容は、Bean Validationのアノテーション（`@Required`, `@Length` など）の `message` 属性とメッセージプロパティファイルで定義します。

参照: `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/handlers/handlers-jaxrs-response-handler.json:s4`, `component/handlers/handlers-jaxrs-response-handler.json:s7`, `component/libraries/libraries-bean-validation.json:s17`