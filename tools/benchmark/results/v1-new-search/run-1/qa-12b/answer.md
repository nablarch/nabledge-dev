**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをユーザーに返すには、`@Valid`アノテーションでバリデーションを有効にし、`ErrorResponseBuilder`のサブクラスを作成してエラーレスポンスのボディにメッセージを設定します。

**根拠**:

**① バリデーションの有効化**

リソースクラスのメソッドに`@Valid`アノテーションを付与します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

バリデーションエラーが発生すると、フレームワークは`ApplicationException`をスローします。

**② エラーメッセージをレスポンスに設定する**

`ErrorResponseBuilder`を継承したクラスを作成し、`ApplicationException`をハンドルしてJSON形式のエラーメッセージをレスポンスボディに設定します。

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

**③ ハンドラへの設定**

作成した`SampleErrorResponseBuilder`を`JaxRsResponseHandler`の`errorResponseBuilder`プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**: `ErrorResponseBuilder`の処理中に例外が発生するとレスポンスが生成できなくなります。カスタマイズ時は`ErrorResponseBuilder`内で例外が発生しない実装を徹底してください。万が一例外が発生した場合、フレームワークはWARNレベルでログを出力し、ステータスコード500のレスポンスを返します。

参照: component/handlers/handlers-jaxrs-response-handler.json:s4, s7, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, processing-pattern/restful-web-service/restful-web-service-feature-details.json:s11