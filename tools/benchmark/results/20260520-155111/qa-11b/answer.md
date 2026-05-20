**結論**: RESTfulウェブサービスでは、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）がエラー処理の中核を担い、例外の種類に応じてHTTPレスポンス生成とログ出力を自動的に行います。

**根拠**:

### エラー処理の仕組み

`JaxRsResponseHandler`（クラス名: `nablarch.fw.jaxrs.JaxRsResponseHandler`）は後続ハンドラ（リソースクラスや`BodyConvertHandler`）で発生した例外・エラーを捕捉し、以下の2つを担います。

**1. レスポンス生成（`errorResponseBuilder`プロパティ）**

`ErrorResponseBuilder`がエラー内容に応じたHTTPレスポンスを生成します。省略時はデフォルト実装が使用されます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

例外クラスが`HttpErrorResponse`の場合は`HttpErrorResponse#getResponse()`から取得したレスポンスがそのまま返却されます。

**2. ログ出力（`errorLogWriter`プロパティ）**

`JaxRsErrorLogWriter`がエラーログを出力します。省略時はデフォルト実装が使用されます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### カスタマイズ例

バリデーションエラー時にJSONメッセージをレスポンスに含めたい場合：

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

特定例外に対して個別のステータスコードを返す場合：

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(final HttpRequest request,
            final ExecutionContext context, final Throwable throwable) {
        if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        } else {
            return super.build(request, context, throwable);
        }
    }
}
```

### グローバルエラーハンドラとの役割分担

`GlobalErrorHandler`（`nablarch.fw.handler.GlobalErrorHandler`）はハンドラキューの先頭に配置され、`JaxRsResponseHandler`でも捕捉できなかった最終的な未捕捉例外を処理します。例外クラスに応じてFATAL/INFOレベルのログを出力します。

**注意点**:
- `ErrorResponseBuilder`のカスタマイズ実装内で例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して処理を継続します。
- `GlobalErrorHandler`はできるだけハンドラキューの先頭に配置してください。

参照: component/handlers/handlers-jaxrs-response-handler.json:s4, component/handlers/handlers-jaxrs-response-handler.json:s5, component/handlers/handlers-jaxrs-response-handler.json:s7, component/handlers/handlers-jaxrs-response-handler.json:s8, component/handlers/handlers-global-error-handler.json:s4, component/handlers/handlers-global-error-handler.json:s5