**結論**: RESTfulウェブサービスで入力チェックエラーをユーザーに返すには、リソースクラスのメソッドに `@Valid` アノテーションを設定してバリデーションをトリガーし、`ErrorResponseBuilder` の継承クラスを作成してエラーレスポンスのボディにメッセージを設定します。

**根拠**:

**① バリデーションの実行**

リソース(アクション)クラスのメソッドに `@Valid` アノテーションを設定するだけで、`JaxRsBeanValidationHandler` がForm(Bean)に対してBean Validationを実行します。バリデーションエラーが発生すると `ApplicationException` が送出されます。

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

バリデーションエラー時にエラーメッセージをレスポンスボディに含めて返すには、`ErrorResponseBuilder` の継承クラスを作成します。

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

作成したクラスは `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージの定義**

バリデーションエラーメッセージは、デフォルトでメッセージ管理（プロパティファイル）から取得されます。アノテーションの `message` 属性に `{メッセージID}` 形式で指定したIDをキーにメッセージを定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**注意点**:
- `ErrorResponseBuilder` の実装中に例外が発生すると、フレームワークはWARNログを出力してステータスコード500のレスポンスを返すため、実装中に例外が発生しないよう注意すること。
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに設定する必要があります。

参照: handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-bean-validation-handler.json:s4, libraries-bean-validation.json:s7, handlers-jaxrs-response-handler.json:s4

---