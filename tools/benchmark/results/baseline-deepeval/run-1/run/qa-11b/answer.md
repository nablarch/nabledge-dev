**結論**: RESTfulウェブサービスでのエラー処理は、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）と`GlobalErrorHandler`（グローバルエラーハンドラ）の2つのハンドラが役割分担している。`JaxRsResponseHandler`がエラーレスポンスの生成・ログ出力・クライアントへの返却を担い、`GlobalErrorHandler`が未捕捉の実行時例外/エラーのログ出力を担う。

**根拠**:

### ハンドラキューにおける位置

最小ハンドラ構成で、この2つのハンドラは以下のように配置される：

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | `GlobalErrorHandler` | 実行時例外またはエラーの場合、ログ出力を行う |
| 2 | `JaxRsResponseHandler` | 例外に対応したレスポンスの生成・書き込み・ログ出力を行う |

---

### JaxRsResponseHandler の役割（エラーレスポンス生成）

後続ハンドラで例外・エラーが発生した場合、`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` によってレスポンスが生成される。

- 例外クラスが `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返される
- それ以外の場合はデフォルト実装の `ErrorResponseBuilder` が使用される
- プロジェクト要件に合わない場合はデフォルト実装を継承してカスタマイズする

設定例：
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

バリデーションエラー時にJSONでエラーメッセージを返す例：
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

特定例外に対して個別のステータスコードを返す例：
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

---

### JaxRsResponseHandler の役割（ログ出力）

ログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` によって行われる。デフォルト実装で要件を満たせない場合はデフォルト実装クラスを継承する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### GlobalErrorHandler の役割（未捕捉例外のログ出力）

`JaxRsResponseHandler` より前段（ハンドラキューの先頭近く）に配置し、未捕捉の例外・エラーをログ出力する：

| 例外/エラークラス | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` によるログ（実装クラスにより異なる） |
| `Result.Error`（サブクラス含む） | FATAL |
| 上記以外の例外 | FATAL |
| `ThreadDeath`（サブクラス含む） | INFO |
| `StackOverflowError`/`OutOfMemoryError` | FATAL |
| その他のエラー | FATAL |

**注意点**:
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること。これより前段のハンドラで例外が発生した場合はウェブアプリケーションサーバやJVMによって処理される。
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して後続処理を継続する。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s3, handlers-global-error-handler.json:s4, restful-web-service-architecture.json:s4

---