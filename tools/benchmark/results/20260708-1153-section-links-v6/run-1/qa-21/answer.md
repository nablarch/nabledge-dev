**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、(1) リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、(2) `ErrorResponseBuilder` を継承したカスタムクラスで `ApplicationException` をJSON等のエラーレスポンスに変換する、という2ステップで実装する。

---

**根拠**:

**ステップ1: バリデーションの実行**

リソース(アクション)クラスのメソッドに `@Valid` アノテーションを設定する。`JaxRsBeanValidationHandler` がバリデーションを実行し、エラー時は `ApplicationException` を送出する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**ステップ2: エラーレスポンスへのメッセージ設定**

デフォルトでは `ErrorResponseBuilder` はメッセージなしのエラーレスポンスを生成する。JSON形式のエラーメッセージをレスポンスに含めるには、`ErrorResponseBuilder` を継承して `ApplicationException` を処理するカスタム実装を作成する。

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

作成したクラスをコンポーネント設定ファイルで `JaxRsResponseHandler` に登録する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**エラーメッセージのプロパティ定義**

デフォルトでは `NablarchMessageInterpolator` がメッセージ管理からメッセージを構築する。アノテーションの `message` 属性に `{messageId}` 形式で指定し、プロパティファイルに定義する。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろのハンドラキューに設定すること。
- `ErrorResponseBuilder` のカスタム実装内で例外が発生すると、フレームワークはWARNログを出力しステータスコード500を返すため、例外が発生しないよう実装すること。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  RESTfulウェブサービスのユーザ入力値のチェックを行う
  バリデーションエラー時のエラーメッセージを定義する
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
- Jakarta RESTful Web Servicesレスポンスハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md
  エラー時のレスポンスにメッセージを設定する
  例外及びエラーに応じたレスポンスの生成