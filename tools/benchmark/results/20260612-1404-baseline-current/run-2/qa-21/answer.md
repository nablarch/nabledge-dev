**結論**: RESTfulウェブサービスでバリデーションエラーをユーザーに返すには、リソースメソッドに`@Valid`アノテーションを付与してバリデーションを実行し、`ErrorResponseBuilder`を継承してエラーメッセージをレスポンスボディに設定します。

**根拠**:

**① バリデーションの実行 — `@Valid`アノテーション**

リソースクラスのメソッドに`@Valid`を付与します。バリデーションエラーが発生すると`ApplicationException`が送出されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージのレスポンス返却 — `ErrorResponseBuilder`の実装**

`ErrorResponseBuilder`を継承し、`ApplicationException`を受け取ったときにエラーメッセージを含むレスポンスを生成します。以下はJSON形式で返却する実装例です。

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

**③ `JaxRsResponseHandler`への登録**

作成した`SampleErrorResponseBuilder`をコンポーネント定義ファイルで`JaxRsResponseHandler`の`errorResponseBuilder`プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `JaxRsBeanValidationHandler`は`リクエストボディ変換ハンドラ`より後ろのハンドラキューに設定する必要があります。
- `ErrorResponseBuilder`の実装中に例外が発生すると、フレームワークはWARNログを出力してステータスコード500を返します。例外が発生しないよう実装してください。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4