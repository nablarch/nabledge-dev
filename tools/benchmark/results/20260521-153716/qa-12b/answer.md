セクション内容を確認できました。回答を生成します。

---

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、①リソースクラスのメソッドに `@Valid` アノテーションを付与してバリデーションを有効化し、②`ErrorResponseBuilder` を継承したクラスを実装してエラーレスポンスのボディにメッセージを設定する。

---

**根拠**:

**ステップ1: バリデーションの有効化**

リソースクラスのメソッドに `@Valid` アノテーションを設定する。`JaxRsBeanValidationHandler` がリクエストボディから変換された Form に対して Bean Validation を実行し、エラー時は `ApplicationException` を送出する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**ステップ2: エラーメッセージをレスポンスに設定**

`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` が送出された場合に JSON 形式のエラーメッセージを含む HTTP 400 レスポンスを返す実装を行う。

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

**ステップ3: コンポーネント設定ファイルへの登録**

作成した `ErrorResponseBuilder` を `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ステップ4: エラーメッセージの定義**

バリデーションエラー時のメッセージは、アノテーションのデフォルト値をメッセージIDとしてプロパティファイルに定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに設定すること（変換後の Form に対してバリデーションを実行するため）
- `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せない状態になるため、例外が発生しないよう実装すること。もし発生した場合はフレームワークが WARN ログを出力してステータスコード 500 を返す

---

参照:
- `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`
- `component/handlers/handlers-jaxrs-bean-validation-handler.json:s3`
- `component/handlers/handlers-jaxrs-response-handler.json:s7`
- `component/handlers/handlers-jaxrs-response-handler.json:s4`
- `component/libraries/libraries-bean-validation.json:s7`
- `component/libraries/libraries-bean-validation.json:s17`

---