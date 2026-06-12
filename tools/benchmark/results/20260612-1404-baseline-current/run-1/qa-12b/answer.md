**結論**: RESTfulウェブサービスでは、リソースクラスのメソッドに `@Valid` アノテーションを付けてBean Validationを実行し、バリデーションエラー時にエラーメッセージをレスポンスボディに返すには `ErrorResponseBuilder` の継承クラスを作成して `JaxRsResponseHandler` に設定します。

**根拠**:

**① バリデーションの有効化（`@Valid` アノテーション）**

リソースクラスのメソッドに `@Valid` を付けるとフレームワークがBean Validationを実行します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージのレスポンスへの設定**

バリデーションエラー発生時は `ApplicationException` がスローされます。このとき `ErrorResponseBuilder` の継承クラスを作成し、JSONエラーメッセージをレスポンスボディに設定します。

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

**③ コンポーネント設定への登録**

作成した `ErrorResponseBuilder` を `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**④ エラーメッセージの定義**

アノテーションの `message` 属性に指定したメッセージIDをプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
```

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生するとレスポンスが生成できなくなるため、カスタマイズ時は例外が発生しないよう実装してください。発生した場合はフレームワークがWARNログを出力しステータスコード500を返します。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, component/libraries/libraries-bean-validation.json:s7