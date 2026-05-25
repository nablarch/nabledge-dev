**結論**: 入力チェック（バリデーション）でエラーが発生したとき、エラーメッセージをユーザーに返す方法はアプリケーションの種類によって異なります。Webアプリケーションでは `ApplicationException` を送出するとフレームワークが自動的に `ErrorMessages` に変換してリクエストスコープに格納します。RESTfulサービスでは `ErrorResponseBuilder` をカスタマイズしてレスポンスボディにメッセージを設定します。

**根拠**:

### Webアプリケーションの場合

バリデーションエラー時は `ApplicationException` を送出します。`HttpErrorHandler` がこれを受け取り、以下の処理を自動実行します。

1. `ApplicationException` が保持するメッセージ情報を `ErrorMessages` に変換する
2. `ErrorMessages` をリクエストスコープのキー `errors` に設定する（View側でエラーメッセージを扱える状態になる）

特定の入力項目に紐づくエラーを表示したい場合（例：メールアドレスの重複チェック）は、`ValidationUtil#createMessageForProperty` を使って項目名付きのエラーメッセージを構築します：

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

リクエストスコープのキー名を変更したい場合は、コンポーネント設定ファイルで変更できます：

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーをmessagesに変更 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### RESTfulサービスの場合

`ErrorResponseBuilder` の継承クラスを作成し、`JaxRsResponseHandler` に設定します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

JSON形式でエラーメッセージを返す実装例：

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

### エラーメッセージの定義

バリデーションアノテーションのメッセージはプロパティファイルで定義します（`{}`で囲むとメッセージ管理を使用）：

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生すると、クライアントにレスポンスを返せなくなります。例外が発生しないよう実装してください（フレームワークはWARNログを出力した後、ステータスコード500のレスポンスを返します）
- Webアプリケーションの `ApplicationException` は `HttpErrorResponse` でラップして送出する必要があります（`HttpErrorHandler` が `HttpErrorResponse` の原因例外が `ApplicationException` の場合に自動変換処理を行います）
- RESTfulサービスで `@Valid` アノテーションを使う場合は `JaxRsBeanValidationHandler` がバリデーションを実行し、エラー時に `ApplicationException` を送出します

参照: `component/handlers/handlers-HttpErrorHandler.json#s4`, `component/handlers/handlers-jaxrs-response-handler.json#s7`, `component/libraries/libraries-bean-validation.json#s13`, `component/libraries/libraries-bean-validation.json#s7`, `component/handlers/handlers-jaxrs-response-handler.json#s4`