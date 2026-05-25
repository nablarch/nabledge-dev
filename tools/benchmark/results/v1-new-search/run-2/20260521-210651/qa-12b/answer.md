Step 5: 回答を生成します。

---

**結論**: リソースクラスのメソッドに `@Valid` アノテーションを付け、`ErrorResponseBuilder` を継承してエラーメッセージ付きのレスポンスを返す実装を行う。

**根拠**:

### 1. バリデーションの実行（`@Valid` アノテーション）

リソース（アクション）クラスのメソッドに `@Valid` を付けると、受け取った Form/Bean に対して Bean Validation が実行される。バリデーションエラーが発生すると `ApplicationException` がスローされる。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 2. エラーメッセージの定義（プロパティファイル）

デフォルトでは `NablarchMessageInterpolator` が使用され、プロパティファイルからメッセージを構築する。アノテーションのデフォルトメッセージIDをキーにして定義する。アノテーションの属性値（`{max}` など）をプレースホルダとして埋め込める。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必ず入力してください。
```

### 3. エラーレスポンスへのメッセージ設定（`ErrorResponseBuilder` の拡張）

`JaxRsResponseHandler` に設定した `ErrorResponseBuilder` がエラーレスポンスを生成する。エラーメッセージをレスポンスボディに含めるには継承クラスを作成する。

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

コンポーネント定義ファイルで `JaxRsResponseHandler` に設定する:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

### 4. 特定項目に紐づくエラーメッセージ（アクション内で手動スロー）

DB重複チェックなどアクションハンドラ内のバリデーションで、特定フィールドのエラーとして返したい場合は `ValidationUtil#createMessageForProperty` を使用する。

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:
- Form/Bean のプロパティは必ず `String` 型で定義すること。`String` 以外の型にすると、不正な値が送信された際にバリデーション前の変換処理が失敗し、予期しない例外が発生する。
- `ErrorResponseBuilder` 内で例外が発生すると、レスポンスを返せずステータス500になる。実装中に例外が発生しないよう注意する。

参照: `handlers-jaxrs-bean-validation-handler.json:s4`, `handlers-jaxrs-response-handler.json:s4`, `handlers-jaxrs-response-handler.json:s7`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s13`

---