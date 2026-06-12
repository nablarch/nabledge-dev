Step 4で読み込んだセクションをもとに回答を生成します。

---

**結論**: リソースクラスのメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、エラーメッセージをレスポンスボディに含めたい場合は `ErrorResponseBuilder` の継承クラスで `ApplicationException` を処理します。

---

**根拠**:

## 1. バリデーションの実行（`@Valid` アノテーション）

リソースクラスのメソッドに `@Valid` を付けると、`JaxRsBeanValidationHandler` がリクエストボディのFormに対してBean Validationを実行します。バリデーションエラー時は `ApplicationException` が送出されます。

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

Formクラスのプロパティはすべて `String` 型で宣言し、バリデーションアノテーションを設定します。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // getter、setterは省略
}
```

## 2. エラーメッセージのレスポンス返却（`ErrorResponseBuilder` の拡張）

デフォルトの `JaxRsResponseHandler` は `ApplicationException` を受け取ってもレスポンスボディにメッセージを設定しません。JSON形式のエラーメッセージをクライアントに返すには、`ErrorResponseBuilder` を継承したクラスを作成します。

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

コンポーネント設定ファイルで `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

## 3. エラーメッセージの定義

バリデーションエラーメッセージは、デフォルトでNablarchのメッセージ管理（プロパティファイル）を使用して構築されます。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

---

**注意点**:
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろにハンドラキューに設定する必要があります
- `ErrorResponseBuilder` の処理中に例外が発生するとレスポンスを返せなくなるため、実装時は例外が発生しないようにすること
- `ApplicationException` から個々のエラーメッセージを取り出す実装は上記コードのコメント部分に入れます

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s7, restful-web-service-getting-started-create.json:s1

---