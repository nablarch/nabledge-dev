Step 5〜8: 回答を生成し、検証して出力します。

---

**結論**: RESTfulウェブサービスでは、**Jakarta RESTful Web Servicesレスポンスハンドラ**（`JaxRsResponseHandler`）がエラーレスポンスの生成とエラーログ出力を担い、**グローバルエラーハンドラ**（`GlobalErrorHandler`）がそれより外側で未捕捉例外・エラーのログ出力を行う2層構造になっている。

---

**根拠**:

### 1. ハンドラキューの構成（最小構成）

最小ハンドラ構成では以下の順でエラー処理が機能する：

| No. | ハンドラ | 例外処理での役割 |
|-----|---------|----------------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | エラーレスポンス生成＋ログ出力 |

### 2. Jakarta RESTful Web Servicesレスポンスハンドラ

エラー発生時の2つの責務を持つ：

**（a）エラーレスポンスの生成**  
`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` がレスポンスを生成する。例外クラスが `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返される。省略時はデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**（b）エラーログの出力**  
`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` がログを出力する。省略時はデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### 3. グローバルエラーハンドラ

`JaxRsResponseHandler` より外側（ハンドラキューの先頭付近）に配置し、未捕捉の例外・エラーをキャッチしてログ出力する：

| 例外・エラー種別 | ログレベル |
|----------------|-----------|
| `ServiceError`（サブクラス含む） | ServiceError の実装クラスによる（`ServiceError#writeLog` を呼び出す） |
| `Result.Error`（サブクラス含む）・その他例外 | FATAL |
| `StackOverflowError`・`OutOfMemoryError`・その他エラー | FATAL |
| `ThreadDeath`・`VirtualMachineError` | INFO（前者）/ FATAL（後者） |

### 4. カスタマイズ例（エラーレスポンスにメッセージを含める）

バリデーションエラー時にJSON形式でエラーメッセージをレスポンスに含めたい場合：

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

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装内で例外が発生すると、フレームワークがその例外を WARNレベルでログ出力し、ステータスコード 500 のレスポンスを生成して処理を継続する。そのため、`ErrorResponseBuilder` の実装内では例外が発生しないよう注意すること。
- グローバルエラーハンドラは原則ハンドラキューの先頭に配置すること。先頭より手前で例外が発生した場合はウェブアプリケーションサーバや JVM による例外処理が行われる。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4

---