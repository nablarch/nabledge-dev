**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをユーザーに返すには、リソースクラスのメソッドに `@Valid` アノテーションを付与してバリデーションを実行し、`ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを設定する。

**根拠**:

**1. バリデーションの実行**

リソースクラスのメソッドに `@Valid` アノテーションを設定する。`JaxRsBeanValidationHandler` がバリデーションを実行し、エラー時は `ApplicationException` を送出する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**2. エラーメッセージのレスポンス設定**

`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` を受け取ってレスポンスボディにメッセージを設定する。

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

作成したクラスを `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**3. エラーメッセージの定義**

デフォルトでは `NablarchMessageInterpolator` がメッセージ管理機能（プロパティファイル）からメッセージを構築する。アノテーションの `message` 属性に `{` `}` で囲んだメッセージIDを指定し、プロパティファイルに定義する。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）より後ろに設定すること（Formへの変換後にバリデーションを行うため）
- `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはWARNレベルでログを出力しステータスコード500のレスポンスを返す

参照:
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
  制約
- Jakarta RESTful Web Servicesレスポンスハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md
  エラー時のレスポンスにメッセージを設定する
  例外及びエラーに応じたレスポンスの生成
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  RESTfulウェブサービスのユーザ入力値のチェックを行う
  バリデーションエラー時のエラーメッセージを定義する