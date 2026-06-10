**結論**: アクションメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、`ErrorResponseBuilder` の継承クラスを作成して `ApplicationException` をJSONエラーレスポンスに変換してクライアントに返します。

---

**根拠**:

#### ステップ1: フォームにバリデーションルールを定義する

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは全て `String` 型で宣言します。

#### ステップ2: アクションメソッドに `@Valid` を付ける

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

`@Valid` アノテーションを設定することで、`JaxRsBeanValidationHandler` がバリデーションを実行します。バリデーションエラー発生時には `ApplicationException` が送出されます。

#### ステップ3: `ErrorResponseBuilder` を継承してエラーレスポンスを実装する

`ApplicationException` をキャッチしてJSONエラーレスポンスに変換します。

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

#### ステップ4: `JaxRsResponseHandler` に `ErrorResponseBuilder` を設定する

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

#### エラーメッセージの定義方法

デフォルトでは `NablarchMessageInterpolator` を使用してメッセージを構築します。アノテーションのメッセージIDをキーにプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
```

---

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生すると、フレームワークはWARNログを出力してステータスコード500のレスポンスを返します。`ErrorResponseBuilder` 内では例外が発生しないよう実装してください。
- 特定の例外（`NoDataException` など）に対して個別のステータスコード（404等）を返したい場合も、同じ `ErrorResponseBuilder` の継承クラスで対応できます。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-bean-validation-handler.json:s4, libraries-bean-validation.json:s7, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1