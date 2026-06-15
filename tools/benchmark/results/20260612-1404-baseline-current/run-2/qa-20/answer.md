**結論**: RESTfulウェブサービスでのエラー処理は、主に **Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）** と **グローバルエラーハンドラ（`GlobalErrorHandler`）** の2つのハンドラが担当する。エラーレスポンスの生成は `ErrorResponseBuilder` が、ログ出力は `JaxRsErrorLogWriter` がそれぞれ担当する。

**根拠**:

### ハンドラキューにおける役割分担

最小ハンドラ構成では以下の順序でエラー処理が機能する：

| No. | ハンドラ | 例外処理の役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・ログ出力 |

### Jakarta RESTful Web Servicesレスポンスハンドラの動作

後続ハンドラで例外・エラーが発生した場合、このハンドラが以下を行う：

**レスポンス生成（`ErrorResponseBuilder`）**
- `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` がエラーレスポンスを生成する
- 発生した例外が `HttpErrorResponse` の場合は、`HttpErrorResponse#getResponse()` で取得した `HttpResponse` をそのままクライアントに返す
- デフォルト実装を使用するか、継承クラスを作成してカスタマイズする

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ログ出力（`JaxRsErrorLogWriter`）**
- `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` がログを出力する
- デフォルト実装を使用するか、継承クラスを作成してカスタマイズする

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### グローバルエラーハンドラの動作

捕捉した例外・エラーの種類に応じてログを出力する：

| 例外/エラークラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力（ログレベルは実装クラス依存）|
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| その他の例外 | FATALレベルでログ出力後、`InternalError` を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルでログ出力後、`InternalError` を返却 |
| `VirtualMachineError` | FATALレベルでログ出力後、エラーをリスロー |

### カスタマイズ例：エラーレスポンスにメッセージを含める

`ApplicationException`（バリデーションエラー）の場合にJSONでエラーメッセージを返す例：

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

### カスタマイズ例：特定の例外に対して個別のステータスコードを返す

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

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装で例外が発生すると、クライアントにレスポンスを返せない状態になる。そのため、`ErrorResponseBuilder` の処理中に例外が発生しないように実装すること（もし発生した場合はフレームワークがWARNレベルでログ出力し、ステータスコード500のレスポンスを返す）
- グローバルエラーハンドラは設定で実装を切り替えられないため、ログレベルを細かく制御したい場合はプロジェクト固有のエラー処理ハンドラを新たに作成すること

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, handlers-global-error-handler.json:s4