**結論**: RESTfulウェブサービスのエラー処理は、**Jakarta RESTful Web Servicesレスポンスハンドラ（JaxRsResponseHandler）** がエラーレスポンス生成とログ出力を担い、その外側の **グローバルエラーハンドラ** が未捕捉例外のログ出力を受け持つ2層構造になっています。

---

**根拠**:

**最小ハンドラ構成（エラー関連の2ハンドラ）**

| No. | ハンドラ | 例外処理での役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | JaxRsResponseハンドラ | 例外に対応したレスポンス生成・書き込み・ログ出力 |

---

**① エラーレスポンスの生成（JaxRsResponseHandler）**

`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が例外の種別に応じてレスポンスを生成します。

- `HttpErrorResponse` が発生した場合 → `HttpErrorResponse#getResponse()` が返す `HttpResponse` をそのままクライアントに返す
- それ以外の例外 → デフォルト実装（`ErrorResponseBuilder`）がレスポンスを生成

カスタマイズ例（バリデーションエラー時にJSONメッセージを返す）:

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
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

設定例:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

---

**② ログ出力（JaxRsResponseHandler）**

`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が例外に応じたログ出力を担います。省略時はデフォルト実装が使用されます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

**③ グローバルエラーハンドラによるログ出力**

`JaxRsResponseHandler` より外側に配置され、未捕捉例外・エラーを捕捉してログを出力します。

| 例外/エラー | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError` の実装クラスによるレベル |
| `Result.Error`（サブクラス含む） | FATAL |
| それ以外の例外 | FATAL（`InternalError` を生成して返却） |
| `ThreadDeath` | INFO（リスロー） |
| `StackOverflowError` / `OutOfMemoryError` | FATAL（`InternalError` を生成して返却） |
| `VirtualMachineError`（上記2つ以外） | FATAL（リスロー） |

グローバルエラーハンドラはできるだけハンドラキューの先頭に配置する必要があります。

---

**注意点**: `ErrorResponseBuilder` をカスタマイズする場合、その処理中に例外が発生するとレスポンスを生成できなくなります。フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して処理を継続します。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4, restful-web-service-architecture.json:s3