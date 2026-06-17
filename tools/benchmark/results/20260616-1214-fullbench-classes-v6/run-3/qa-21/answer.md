**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、(1) リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、(2) `ErrorResponseBuilder` を継承してエラーメッセージをレスポンスボディに含める実装を追加します。

**根拠**:

**① バリデーションの実行（`@Valid` アノテーション）**

リソースクラスのメソッドに `@Valid` を付けると、`JaxRsBeanValidationHandler` がリクエストボディをバインドした Form に対して Bean Validation を実行します。バリデーションエラーが発生した場合、`ApplicationException` がスローされます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

Form クラスには Bean Validation アノテーションを付けてバリデーションルールを定義します。

```java
public class SampleForm {
    @Length(max = 10)
    @Required
    private String userName;
    // getter、setter は省略
}
```

**② エラーメッセージの定義（プロパティファイル）**

エラーメッセージはプロパティファイルで定義します（デフォルトでは Nablarch のメッセージ管理機能を使用）。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**③ エラーレスポンスボディへのメッセージ設定（`ErrorResponseBuilder` の継承）**

デフォルトの `JaxRsResponseHandler` はエラーレスポンスにメッセージボディを含めません。JSON 形式でエラーメッセージを返すには `ErrorResponseBuilder` を継承したクラスを作成します。

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

作成したクラスをコンポーネント設定ファイルに登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生するとクライアントにレスポンスを返せなくなるため、例外が発生しないよう実装すること。
- Form クラスのプロパティはすべて `String` 型で定義すること（数値型などにすると変換失敗で予期せぬ例外が発生する）。
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろに設定すること。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17