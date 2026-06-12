必要な情報が揃いました。Step 5: 回答生成に進みます。

**sections_content のまとめ:**

- `handlers-jaxrs-bean-validation-handler.json:s4` — `@Valid`アノテーションでバリデーション実行
- `component/libraries/libraries-bean-validation.json:s17` — RESTfulのバリデーション方法（s4への参照のみ）
- `handlers-jaxrs-response-handler.json:s4` — ErrorResponseBuilderによるレスポンス生成
- `handlers-jaxrs-response-handler.json:s7` — エラーメッセージをレスポンスに設定する実装例（ApplicationException → 400 + JSONボディ）
- `restful-web-service-getting-started-create.json:s1` — `@Valid`を使った登録機能の実装例
- `javadoc-nablarch-fw-jaxrs-ErrorResponseBuilder.json:s2` — ErrorResponseBuilderのbuildメソッド仕様

**Step 6: Verify**

主要クレーム:
1. `@Valid`アノテーションをリソースメソッドに設定するとバリデーションが実行される → s4(handlers-jaxrs-bean-validation-handler)で明示的に述べられている ✅
2. `ErrorResponseBuilder`を継承してエラーレスポンスにメッセージを設定する → s7で述べられている ✅
3. `ApplicationException`の場合にステータス400でJSONを返す → s7のコード例、およびjavadocのs2で述べられている ✅
4. `JaxRsResponseHandler`の`errorResponseBuilder`プロパティにカスタムクラスを設定する → s4で述べられている ✅

→ `verify_result = PASS`

---

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、①リソースメソッドに`@Valid`アノテーションを付けてバリデーションを実行し、②`ErrorResponseBuilder`を継承したカスタムクラスを作成してエラーメッセージをレスポンスボディに設定します。

---

**結論**: `@Valid`アノテーションでバリデーションを実行し、`ErrorResponseBuilder`を継承したクラスでエラーメッセージ付きレスポンスを生成する。

**根拠**:

**① リソースメソッドに `@Valid` アノテーションを付ける**

バリデーションを実行したいメソッドに `@Valid` アノテーションを設定する。

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid  // ← これを設定するとバリデーションが実行される
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

フォームクラスにはBean Validationのアノテーションでバリデーションルールを定義する。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**② `ErrorResponseBuilder` を継承してエラーメッセージを返す**

バリデーションエラー（`ApplicationException`）が発生したとき、デフォルトの`ErrorResponseBuilder`はステータス400のレスポンスを返すだけで、エラーメッセージをボディに含めない。エラーメッセージをJSON形式でクライアントに返したい場合は、`ErrorResponseBuilder`を継承したクラスを作成する。

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

作成したクラスは `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生するとクライアントにレスポンスを返せない状態になる。カスタムクラス内では例外が発生しないよう実装すること。
- `ApplicationException` 以外の例外は `super.build()` に委譲するとデフォルト動作（ステータス500）が維持される。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, restful-web-service-getting-started-create.json:s1

---