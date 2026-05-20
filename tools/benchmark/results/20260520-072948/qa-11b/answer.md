**結論**: RESTfulウェブサービスのエラー処理は、主に `JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）と `GlobalErrorHandler`（グローバルエラーハンドラ）の2つのハンドラが担う。エラーレスポンスの生成は `ErrorResponseBuilder`、ログ出力は `JaxRsErrorLogWriter` が行い、いずれもカスタマイズ可能。

**根拠**:

### ハンドラ構成（最小ハンドラ構成での役割）

| No. | ハンドラ | エラー時の処理 |
|---|---|---|
| 1 | `GlobalErrorHandler` | 実行時例外・エラーを捕捉し、FATALレベルのログ出力 |
| 2 | `JaxRsResponseHandler` | 例外に対応したレスポンス生成・ログ出力・クライアントへの返却 |

### エラーレスポンスの生成

`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` がレスポンスを生成する。例外クラスが `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の結果がそのままクライアントに返却される。

設定を省略するとデフォルト実装が使用される。カスタマイズする場合は継承クラスを作成して設定する：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

バリデーションエラー時にJSONでメッセージを返す実装例：

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

特定の例外に対して個別のステータスコードを返したい場合：

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

### ログ出力

`JaxRsResponseHandler` の `errorLogWriter` プロパティに `JaxRsErrorLogWriter` を設定する。省略時はデフォルト実装が使用される：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### グローバルエラーハンドラによる補完

`GlobalErrorHandler`（クラス名: `nablarch.fw.handler.GlobalErrorHandler`）はハンドラキューの先頭に配置し、`JaxRsResponseHandler` で処理されなかった実行時例外・エラーを捕捉する：

| 例外/エラー | ログ出力 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出し（レベルは実装クラスに依存） |
| `Result.Error`（サブクラス含む） | FATALレベル |
| その他の例外 | FATALレベル |
| `ThreadDeath` | INFOレベル |
| `StackOverflowError` / `OutOfMemoryError` / `VirtualMachineError` | FATALレベル |

### アクセスログ

`JaxRsAccessLogHandler`（クラス名: `nablarch.fw.jaxrs.JaxRsAccessLogHandler`）をハンドラキューに追加することで、リクエスト処理開始時・終了時のHTTPアクセスログ（ロガー名: `HTTP_ACCESS`、INFOレベル）を出力できる。

**注意点**:
- `ErrorResponseBuilder` 処理中に例外が発生すると、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して処理を継続する。そのため `ErrorResponseBuilder` のカスタマイズ時は処理中に例外が発生しないよう実装すること。
- `GlobalErrorHandler` はログレベルの細かい切り替えなど要件を満たせない場合、設定で切り替えられないためプロジェクト固有のエラー処理ハンドラを新たに作成して対応すること。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, restful-web-service-architecture.json:s4, handlers-global-error-handler.json:s4, handlers-jaxrs-access-log-handler.json:s4