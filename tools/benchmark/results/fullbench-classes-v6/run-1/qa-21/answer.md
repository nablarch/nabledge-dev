**結論**: RESTfulウェブサービスでバリデーションエラーが発生した場合、リソースメソッドに`@Valid`アノテーションを設定してバリデーションを実行し、`ErrorResponseBuilder`を継承したクラスでエラーメッセージをJSONレスポンスに設定して返す。

---

**根拠**:

**1. バリデーションの実行**

リソース(アクション)クラスのメソッドに`@Valid`アノテーションを付与することで、`JaxRsBeanValidationHandler`がForm(Bean)に対してBean Validationを実行する。バリデーションエラー発生時は後続処理に委譲せず`ApplicationException`が送出される。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

**2. エラーメッセージのレスポンス返却**

`ErrorResponseBuilder`を継承したクラスを作成し、`ApplicationException`発生時にエラーメッセージをJSON形式でレスポンスボディに設定する。

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

**3. コンポーネント設定**

作成した`SampleErrorResponseBuilder`を`JaxRsResponseHandler`の`errorResponseBuilder`プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

---

**注意点**:
- `ErrorResponseBuilder`の処理中に例外が発生するとクライアントにレスポンスを返せなくなるため、例外が発生しないよう実装すること。
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろに設定すること（リクエストボディ変換後にバリデーションを行うため）。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s17, restful-web-service-getting-started-create.json:s1