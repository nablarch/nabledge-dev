**結論**: RESTfulウェブサービスでのエラー処理は、主に **`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）** と **`GlobalErrorHandler`（グローバルエラーハンドラ）** の2つのハンドラが担う。エラーレスポンスの生成は `ErrorResponseBuilder`、ログ出力は `JaxRsErrorLogWriter` がそれぞれ担当する。

---

**根拠**:

#### ハンドラの役割分担

最小ハンドラ構成における2つのエラー処理ハンドラの役割は以下の通り。

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | `GlobalErrorHandler` | 実行時例外・Errorの場合にログ出力 |
| 2 | `JaxRsResponseHandler` | 例外(エラー)に対応したレスポンス生成・書き込み・ログ出力 |

#### JaxRsResponseHandler の仕組み

後続ハンドラ（アクションクラスなど）で例外が発生した際に、エラーレスポンスとログを処理する中心的なハンドラ。

**エラーレスポンス生成**:  
`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が生成を担当する。例外が `HttpErrorResponse` の場合は、その中の `HttpResponse` が直接クライアントに返される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**エラーログ出力**:  
`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` がログ出力を担当する。デフォルト実装では `FailureLogUtil` を用いてログ出力を行う。`ApplicationException`（バリデーションエラー等）の場合はデフォルトでログ出力しない（`writeApplicationExceptionLog` は何もしない）。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

#### GlobalErrorHandler の仕組み

未捕捉の例外・エラーを捕捉して処理する。ハンドラキューの先頭（最前）に配置する。

| 例外・エラークラス | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | 実装クラスに依存（`ServiceError#writeLog` 呼び出し） |
| `Result.Error`（サブクラス含む） | FATAL |
| それ以外の例外 | FATAL |
| `ThreadDeath` / `VirtualMachineError` | INFO / FATAL（リスロー） |
| `StackOverflowError` / `OutOfMemoryError` | FATAL |

#### カスタマイズ

エラーレスポンスにメッセージを含めたい場合は、`ErrorResponseBuilder` を継承して `build` メソッドをオーバーライドする。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            // バリデーションエラー → 400 + JSON ボディ
            return createResponseBody((ApplicationException) throwable);
        } else if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        } else {
            return super.build(request, context, throwable);
        }
    }
}
```

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装の中で例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを返す。そのため `ErrorResponseBuilder` 内では例外が発生しない実装を徹底すること。
- `GlobalErrorHandler` より前に配置したハンドラで例外が発生した場合、ウェブアプリケーションサーバやJVMによって処理されるため、Nablarchのエラー処理は適用されない。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, restful-web-service-architecture.json:s4, javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json:s4