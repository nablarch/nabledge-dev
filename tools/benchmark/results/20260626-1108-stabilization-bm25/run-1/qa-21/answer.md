**結論**: RESTfulウェブサービスで入力チェックエラー時にエラーメッセージをユーザーに返すには、(1) リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、(2) `ErrorResponseBuilder` を継承したクラスを作成して `ApplicationException` 発生時にエラーメッセージをレスポンスボディに設定します。

---

**根拠**

**① バリデーションの実行（`@Valid` アノテーション）**

入力値を受け取るリソースクラスのメソッドに `@Valid` を付けると、JaxRsBeanValidationHandler がフォームクラスに対してバリデーションを実行します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージのレスポンス返却（`ErrorResponseBuilder` のカスタマイズ）**

バリデーションエラーが発生すると `ApplicationException` がスローされます。このとき `JaxRsResponseHandler` の `errorResponseBuilder` プロパティにカスタム実装を設定することで、エラーメッセージをレスポンスボディに含めて返却できます。

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

コンポーネント定義ファイルへの設定：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージの定義（プロパティファイル）**

バリデーションアノテーションに対応するメッセージはプロパティファイルで定義します。デフォルトでは `NablarchMessageInterpolator` が使用され、アノテーションの `message` 属性に `{...}` 形式でメッセージIDを指定することでメッセージ管理と連携します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須入力です。
```

---

**注意点**

- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろに配置する必要があります。
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生すると、クライアントにレスポンスを返せなくなります。実装時は例外が発生しないよう注意してください（発生した場合はフレームワークが WARNING ログを出力してステータスコード 500 を返します）。

参照:
- `libraries-bean-validation.json:s17`
- `libraries-bean-validation.json:s7`
- `libraries-bean-validation.json:s6`
- `handlers-jaxrs-bean-validation-handler.json:s4`
- `handlers-jaxrs-response-handler.json:s7`
- `handlers-jaxrs-response-handler.json:s4`