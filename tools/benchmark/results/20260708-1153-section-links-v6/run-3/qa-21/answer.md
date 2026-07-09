**結論**: リソースメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、`ErrorResponseBuilder` の継承クラスを作成して `ApplicationException` からエラーメッセージをレスポンスボディに組み込む。

**根拠**:

**ステップ1: リソースメソッドに `@Valid` アノテーションを設定**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

これにより `JaxRsBeanValidationHandler` がバリデーションを実行し、エラー時は `ApplicationException` を送出する。

**ステップ2: エラーメッセージのプロパティファイル定義**

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

デフォルトでは `NablarchMessageInterpolator` がメッセージ管理を使用してメッセージを構築する。`message` 属性の値を `{` `}` で囲んで定義すること。

**ステップ3: `ErrorResponseBuilder` を継承してエラーレスポンスを実装**

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

**ステップ4: `JaxRsResponseHandler` に `ErrorResponseBuilder` を設定**

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `JaxRsBeanValidationHandler` はリクエストボディ変換ハンドラ (`BodyConvertHandler`) よりも後ろに設定すること
- `ErrorResponseBuilder` の実装中に例外が発生しないよう注意すること（発生した場合、WARNログ出力後にステータスコード500のレスポンスが生成される）

参照:
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
- Jakarta RESTful Web Servicesレスポンスハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md
  エラー時のレスポンスにメッセージを設定する
  例外及びエラーに応じたレスポンスの生成
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションエラー時のエラーメッセージを定義する
  RESTfulウェブサービスのユーザ入力値のチェックを行う