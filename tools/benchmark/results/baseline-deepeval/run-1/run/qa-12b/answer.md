**結論**: リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、`ErrorResponseBuilder` を継承したクラスを実装してエラーレスポンスのボディにメッセージを設定して返す。

**根拠**:

**① バリデーションの実行**

リソースクラスのメソッドに `@Valid` アノテーションを付けると、受け取った Form/Bean に対してバリデーションが実行される。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージの定義**

バリデーションエラー時のメッセージは、アノテーションの `message` 属性に指定したメッセージIDをキーとして、プロパティファイルに定義する。

```java
public class SampleForm {
  @Length(max = 10)
  @Required
  private String userName;
  // getter、setterは省略
}
```

```properties
# Lengthアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
```

**③ エラーレスポンスへのメッセージ設定**

`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` に対してエラーメッセージをJSON形式でレスポンスボディに設定する。

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

作成した `SampleErrorResponseBuilder` をコンポーネント定義ファイルに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- Jakarta RESTful Web Services Bean Validationハンドラは、リクエストボディ変換ハンドラよりも後ろに配置すること（変換後の Bean に対してバリデーションを行うため）
- `ErrorResponseBuilder` の処理中に例外が発生すると、クライアントにレスポンスを返せない状態になるため、カスタマイズ時は例外が発生しないよう実装すること

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s6, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17

---