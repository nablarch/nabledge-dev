Step 5で回答を生成します。

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、(1) リソースメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、(2) `ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを設定する実装を追加します。

**根拠**:

**① バリデーションの設定（JaxRsBeanValidationHandlerの利用）**

リソースクラスのメソッドに `@Valid` アノテーションを付与することで、ハンドラが自動的にBean Validationを実行します。エラー時は `ApplicationException` が送出されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージをレスポンスに設定する**

`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに `ErrorResponseBuilder` の継承クラスを設定します。`ApplicationException` を受け取ってJSON形式でエラーメッセージを返す実装例を示します。

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

コンポーネント設定ファイルで登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージの定義**

バリデーションアノテーションの `message` 属性をメッセージIDとしてプロパティファイルに定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**注意点**:
- `JaxRsBeanValidationHandler` はリクエストボディ変換ハンドラ（`BodyConvertHandler`）より後ろに設定すること。
- `ErrorResponseBuilder` の実装中に例外が発生するとレスポンスを返せない状態になるため、例外が発生しないよう実装すること（発生した場合はフレームワークがWARNログを出してステータス500を返す）。
- FormクラスのプロパティはすべてString型として定義すること。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17