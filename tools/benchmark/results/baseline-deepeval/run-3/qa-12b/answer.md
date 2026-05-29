セクション内容が揃いました。回答を生成します。

---

**結論**: リソースクラスのメソッドに `@Valid` アノテーションを付与してバリデーションを実行し、`ErrorResponseBuilder` を継承したクラスを実装してエラーレスポンスにメッセージを設定する。

**根拠**:

**① バリデーションの実行（@Valid アノテーション）**

入力値を受け取るリソースクラスのメソッドに `@Valid` を付与する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージをレスポンスに含める（ErrorResponseBuilder の実装）**

`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` 発生時にエラーメッセージを含む JSON レスポンスを返す。

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

**③ コンポーネント設定ファイルへの登録**

`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに実装クラスを設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**④ エラーメッセージのプロパティファイル定義**

デフォルトでは `NablarchMessageInterpolator` がメッセージ管理を使用する。アノテーションに対応するメッセージはプロパティファイルで定義する。

```properties
# Lengthアノテーションに対応したメッセージ
nablarch.core.validation.ee.Length.min.message={min}文字以上で入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
```

**注意点**:
- Form（Bean）のプロパティはすべて `String` 型として定義すること。`String` 以外の型（数値型など）を使用すると、不正な値が入力された際にバリデーション前の変換処理が失敗し、予期せぬ例外が発生する
- `ErrorResponseBuilder` の処理中に例外が発生しないよう実装すること。例外が発生した場合、フレームワークは WARN ログを出力してステータスコード 500 のレスポンスを返す

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17

---