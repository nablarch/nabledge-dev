**結論**: RESTfulウェブサービスでバリデーションエラーメッセージをユーザーに返すには、`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` を受け取ったときにエラーメッセージをレスポンスボディに設定して返すよう実装します。

**根拠**:

バリデーションエラーが発生すると、`JaxRsBeanValidationHandler` が `ApplicationException` を送出します。この例外は `JaxRsResponseHandler` の `errorResponseBuilder` で捕捉されるため、以下のように `ErrorResponseBuilder` の継承クラスを作成します。

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

作成したクラスをコンポーネント設定ファイルで `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

また、バリデーション実行にはリソースクラスのメソッドに `@Valid` アノテーションを付与します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せない状態になります。カスタマイズする場合は、処理中に例外が発生しないよう実装してください。なお例外が発生した場合、フレームワークはWARNレベルでログ出力を行い、ステータスコード500のレスポンスを生成します。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-bean-validation-handler.json:s4