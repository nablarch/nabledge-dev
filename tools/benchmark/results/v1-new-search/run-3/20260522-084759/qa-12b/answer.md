セクション内容を確認しました。回答を生成します。

---

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントへ返すには、(1) リソースクラスのメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、(2) `ErrorResponseBuilder` を継承したクラスを作成してエラーレスポンスのボディにメッセージを設定する。

---

**根拠**:

### 1. バリデーションの実行 — `@Valid` アノテーション

リソースクラスのメソッドに `@Valid` を設定すると、`JaxRsBeanValidationHandler` がリクエストボディをバインドしたFormに対してBean Validationを実行する。エラーがあれば `ApplicationException` が送出される。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 2. エラーメッセージをレスポンスに設定 — `ErrorResponseBuilder` の継承

`JaxRsResponseHandler` は発生した例外を `ErrorResponseBuilder` に渡してレスポンスを生成する。エラーメッセージをレスポンスボディに含めたい場合は `ErrorResponseBuilder` を継承する。

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

作成したクラスをコンポーネント設定ファイルに登録する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

### 3. エラーメッセージの定義

バリデーションエラーのメッセージはデフォルトでメッセージ管理（プロパティファイル）を使用して構築される。アノテーションの `message` 属性に `{メッセージID}` 形式で指定する。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

---

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはWARNレベルでログを出力し、ステータスコード500のレスポンスを生成する。そのため、`ErrorResponseBuilder` の実装内で例外が発生しないように実装すること。
- `JaxRsBeanValidationHandler` は `リクエストボディ変換ハンドラ` よりも後ろに設定する必要がある。

参照: `handlers-jaxrs-bean-validation-handler.json:s4`, `handlers-jaxrs-response-handler.json:s7`, `handlers-jaxrs-response-handler.json:s4`, `libraries-bean-validation.json:s7`

---