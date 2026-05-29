Step 5と6: 回答を生成し、検証します。

---

**結論**: リソースクラスのメソッドに `@Valid` アノテーションを付与してバリデーションを実行し、`ErrorResponseBuilder` のサブクラスを実装して `ApplicationException` からエラーメッセージを取り出しJSONレスポンスとして返す。

**根拠**:

**1. Formクラスにバリデーションアノテーションを設定する**

Formのプロパティはすべて `String` 型で定義し、`@Required`・`@Length` などのアノテーションを付与する。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterは省略
}
```

**2. リソースクラスのメソッドに `@Valid` を付与する**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

バリデーションエラーが発生すると、`JaxRsBeanValidationHandler` が `ApplicationException` をスローする。

**3. `ErrorResponseBuilder` を継承してエラーレスポンスを構築する**

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

**4. エラーメッセージをプロパティファイルに定義する**

アノテーションのデフォルトメッセージIDをキーにしてメッセージを定義する。

```properties
nablarch.core.validation.ee.Length.min.message={min}文字以上で入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formのプロパティは **必ずすべて `String` 型** で定義すること。`String` 以外の型が含まれていると、不正な値が送信された際にBeanへの変換処理が失敗し、バリデーション結果を返す前に障害となる。
- エラーメッセージに項目名を含めたい場合は、コンポーネント設定で `ItemNamedConstraintViolationConverterFactory` を `constraintViolationConverterFactory` という名前で設定する。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s7, libraries-bean-validation.json:s8

---