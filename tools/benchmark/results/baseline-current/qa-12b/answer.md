**結論**: RESTfulウェブサービスでバリデーションエラー発生時にエラーメッセージをユーザーに返すには、`ErrorResponseBuilder` を継承したカスタムクラスを作成し、`JaxRsResponseHandler` に設定します。

**根拠**:

**1. リソースメソッドに `@Valid` を付与してバリデーションを有効化**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

`@Valid` を付与することで、リクエストの Form (Bean) に対してバリデーションが実行されます。

**2. `ErrorResponseBuilder` を継承してエラーメッセージをレスポンスに設定**

バリデーションエラーは `ApplicationException` としてスローされます。これを受け取ってエラーメッセージを JSON 形式でレスポンスボディに設定します。

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

**3. コンポーネント設定でカスタム `ErrorResponseBuilder` を登録**

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:

- `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せなくなるため、カスタム実装では例外が発生しないよう実装すること
- 万が一 `ErrorResponseBuilder` 内で例外が発生した場合、フレームワークは WARN レベルでログ出力し、ステータスコード 500 のレスポンスを返す
- `ApplicationException` 以外の例外（例: `NoDataException` → 404）は、`super.build()` に委譲するか、別途個別処理を追加する

参照: `component/handlers/handlers-jaxrs-response-handler.json#s7`, `component/handlers/handlers-jaxrs-response-handler.json#s4`, `component/handlers/handlers-jaxrs-bean-validation-handler.json#s4`