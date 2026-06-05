セクション内容を確認しました。Step 5で回答を生成します。

**結論**: RESTfulウェブサービスでバリデーションエラーのメッセージをクライアントに返すには、リソースメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、`ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを含める実装をする。

**Verify**: 回答内のNablarch固有の主張を確認します。

| クレーム | 根拠セクション | 判定 |
|---------|------------|-----|
| `@Valid` アノテーションでバリデーション実行 | handlers-jaxrs-bean-validation-handler.json:s4 | 支持 |
| バリデーションエラー時に `ApplicationException` が送出される | handlers-jaxrs-bean-validation-handler.json 本文 | 支持 |
| `ErrorResponseBuilder` 継承でエラーレスポンスにメッセージを設定 | handlers-jaxrs-response-handler.json:s7 | 支持 |
| `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定 | handlers-jaxrs-response-handler.json:s4 | 支持 |
| メッセージはプロパティファイルに定義する | libraries-bean-validation.json:s7 | 支持 |

`verify_result = PASS` → `final_answer = answer_text`

---

**結論**: リソースメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、`ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを含めます。

**根拠**:

### Step 1: リソースメソッドに `@Valid` を付ける

`JaxRsBeanValidationHandler` が、`@Valid` アノテーションが付いたメソッドの引数FormにBean Validationを実行します。エラーがあれば `ApplicationException` を送出します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### Step 2: エラーメッセージをプロパティファイルに定義する

`NablarchMessageInterpolator`（デフォルト）はアノテーションの `message` 属性のメッセージIDをキーにメッセージを構築します。

```properties
# Requiredアノテーションのメッセージ定義例
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

### Step 3: `ErrorResponseBuilder` を継承してレスポンスにメッセージを含める

デフォルトの `ErrorResponseBuilder` はメッセージをレスポンスボディに含めません。`ApplicationException` を受け取って JSON レスポンスを生成するカスタム実装を作成します。

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

作成したクラスを `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生した場合、WARNログが出力されてステータスコード500のレスポンスが返されます。カスタム実装では例外が発生しないよう実装してください。
- `@Valid` のバリデーション前のリクエストを受け取るFormのプロパティはすべて `String` 型にしてください。String以外の型があると、バリデーション前の変換処理が失敗して予期せぬ例外が発生します。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s7

---