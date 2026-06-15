**結論**: RESTfulウェブサービスでバリデーションエラーメッセージをユーザーに返すには、`JaxRsBeanValidationHandler` を用いてバリデーションを実行し、`ErrorResponseBuilder` を継承したクラスで `ApplicationException` を捕捉してJSON形式のエラーレスポンスを返す。

**根拠**:

#### 1. バリデーションの設定（リソースクラス側）

リソース（アクション）クラスのメソッドに `@Valid` アノテーションを設定することで、リクエストボディのBeanに対してBean Validationが実行される。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(PersonForm form) {
    UniversalDao.insert(form);
    return new HttpResponse();
}
```

バリデーションエラーが発生すると、`JaxRsBeanValidationHandler` が `ApplicationException` を送出して処理を終了する。

#### 2. エラーメッセージをレスポンスに設定する（`ErrorResponseBuilder` の拡張）

`ApplicationException` を捕捉して、JSONエラーレスポンスを返すには `ErrorResponseBuilder` を継承したクラスを作成する。

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

#### 3. コンポーネント定義ファイルへの設定

作成した `SampleErrorResponseBuilder` を `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

#### 4. エラーメッセージの定義（properties ファイル）

バリデーションアノテーションに対応するメッセージをプロパティファイルで定義する。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- Formクラスのプロパティは必ず `String` 型にすること。String以外の型が含まれると、リクエストボディのBean変換時に予期せぬ例外が発生する場合がある。
- `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはWARNログを出力しステータスコード500を返すため、`ErrorResponseBuilder` 内では例外が発生しないよう実装すること。
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに配置すること。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17