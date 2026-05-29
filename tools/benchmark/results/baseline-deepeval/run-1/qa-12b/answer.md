必要な情報が揃いました。回答を生成します。

---

**結論**: RESTfulウェブサービスで入力チェックエラー時にエラーメッセージをクライアントに返すには、①リソースクラスのメソッドに `@Valid` アノテーションを付与してバリデーションを有効化し、②`ErrorResponseBuilder` の継承クラスを作成して `ApplicationException` 発生時にエラーメッセージをレスポンスボディに設定する。

---

**根拠**:

### 1. バリデーションの有効化（`@Valid` アノテーション）

リソースクラスのメソッドに `@Valid` アノテーションを付与すると、`JaxRsBeanValidationHandler` がリクエストボディから変換した Form に対して Bean Validation を実行する。エラー時は `ApplicationException` を送出して処理を終了する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 2. エラーメッセージをレスポンスボディに設定する（`ErrorResponseBuilder` の拡張）

デフォルトの `ErrorResponseBuilder` はエラーメッセージをレスポンスに含めない。JSON 形式のエラーメッセージをクライアントに返したい場合は、継承クラスを作成して `ApplicationException` を処理する。

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

このクラスをコンポーネント設定ファイルに登録する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

### 3. エラーメッセージの定義

バリデーションアノテーションのメッセージは、プロパティファイルに定義する。デフォルトでは `NablarchMessageInterpolator` が使用され、`{` `}` で囲まれた値をメッセージIDとして解決する。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

---

**注意点**:
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに配置する必要がある
- `ErrorResponseBuilder` の処理中に例外が発生するとレスポンスを返せなくなるため、実装時は例外が発生しないよう注意すること（発生した場合はフレームワークが WARN ログを出力しステータス 500 を返す）

参照: `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/handlers/handlers-jaxrs-response-handler.json:s7`, `component/handlers/handlers-jaxrs-response-handler.json:s4`, `component/libraries/libraries-bean-validation.json:s7`

---