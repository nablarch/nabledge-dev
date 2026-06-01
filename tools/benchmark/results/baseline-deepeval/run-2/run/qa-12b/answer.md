**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをユーザーに返すには、2つの対応が必要です。①リソースクラスのメソッドに `@Valid` アノテーションを設定してバリデーションを有効化し、②`ErrorResponseBuilder` を継承したクラスを作成してエラーレスポンスのボディにメッセージを設定します。

---

**根拠**:

**① バリデーションの有効化 — `@Valid` アノテーション**

リソース(アクション)クラスのメソッドに `@Valid` を設定すると、`JaxRsBeanValidationHandler` が受け取った Form(Bean) に対して Bean Validation を実行します。エラーが発生した場合は `ApplicationException` が送出されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーレスポンスへのメッセージ設定 — `ErrorResponseBuilder` の継承**

バリデーションエラー時にレスポンスボディにメッセージを含めるには、`ErrorResponseBuilder` を継承したクラスを作成します。`ApplicationException` をハンドリングして JSON 形式のエラーメッセージをレスポンスに書き込む実装例は以下のとおりです。

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

作成した `SampleErrorResponseBuilder` は `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージの定義**

バリデーションエラー時のメッセージは、デフォルトで `NablarchMessageInterpolator` がメッセージ管理機能を使ってプロパティファイルから構築します。アノテーションの `message` 属性に `{メッセージID}` 形式でメッセージIDを指定します。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せなくなります。カスタマイズ時は例外が発生しないよう実装してください。
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに設定する必要があります。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s17, libraries-bean-validation.json:s7

---