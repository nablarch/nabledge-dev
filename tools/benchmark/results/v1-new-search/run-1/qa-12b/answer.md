これで回答を生成できます。

---

**結論**: RESTfulウェブサービスで入力チェックエラーをユーザーに返すには、①リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、②`ErrorResponseBuilder` を継承したカスタムクラスでエラーメッセージ入りのレスポンスを構築して返します。

**根拠**:

### ① バリデーションの実行（`@Valid` アノテーション）

`JaxRsBeanValidationHandler` がリソースメソッドに付与された `@Valid` を検知し、Bean Validation を実行します。エラーが発生すると `ApplicationException` を送出します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### ② エラーメッセージをレスポンスボディに含める

`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに、`ErrorResponseBuilder` を継承したカスタムクラスを設定します。

**カスタム ErrorResponseBuilder の実装例（JSON形式でエラーメッセージを返す）**:

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

**コンポーネント設定ファイルへの登録**:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

### ③ エラーメッセージの定義

エラーメッセージはプロパティファイルに定義します。デフォルトでは `NablarchMessageInterpolator` が使用され、アノテーションの `message` 属性に `{messageId}` の形式で指定したIDをキーにメッセージを解決します。

```properties
# Lengthアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。

# SystemCharに対応したメッセージ
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生すると、フレームワークはステータスコード500のレスポンスを返してWARNログを出力します。カスタマイズ時は例外が発生しないよう実装してください。

参照: `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/handlers/handlers-jaxrs-response-handler.json:s7`, `component/handlers/handlers-jaxrs-response-handler.json:s4`, `component/libraries/libraries-bean-validation.json:s7`

---