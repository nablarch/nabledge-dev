**結論**: RESTfulウェブサービスのエラー処理は `JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）が中心となり、例外の種類に応じたレスポンス生成とログ出力をそれぞれ独立した仕組みで担う。

---

**根拠**:

### レスポンス生成（エラー画面相当）

レスポンスの生成は `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が担う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

- 発生した例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` が直接クライアントに返される
- 設定を省略するとデフォルト実装の `ErrorResponseBuilder` が使用される

バリデーションエラー時に JSON エラーメッセージを返す場合などは `ErrorResponseBuilder` を継承してカスタマイズする。

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
    // ...
}
```

### ログ出力

ログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

設定を省略するとデフォルト実装が使用される。

### グローバルエラーハンドラによる補完

`JaxRsResponseHandler` では捕捉できない例外・エラーは `GlobalErrorHandler`（グローバルエラーハンドラ）が処理する。例外の種類に応じたログレベルが決まっている。

| 例外・エラーの種類 | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` による（実装依存） |
| `Result.Error`（サブクラス含む） | FATAL |
| 上記以外の例外 | FATAL（`InternalError` に変換して返却） |
| `ThreadDeath` | INFO（リスロー） |
| `StackOverflowError` / `OutOfMemoryError` | FATAL（`InternalError` に変換） |
| その他の `VirtualMachineError` | FATAL（リスロー） |

### アクセスログ

アクセスログは `JaxRsAccessLogHandler` が出力する。ロガー名 `HTTP_ACCESS`、ログレベル INFO でアプリケーションログに出力される。

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはその例外を WARN レベルでログ出力し、ステータスコード 500 のレスポンスを生成して処理を継続する。カスタマイズ時は `ErrorResponseBuilder` 内で例外が発生しないよう実装すること。

参照:
- `component/handlers/handlers-jaxrs-response-handler.json:s4`
- `component/handlers/handlers-jaxrs-response-handler.json:s5`
- `component/handlers/handlers-jaxrs-response-handler.json:s7`
- `component/handlers/handlers-jaxrs-response-handler.json:s8`
- `component/handlers/handlers-global-error-handler.json:s4`
- `component/handlers/handlers-global-error-handler.json:s5`
- `component/libraries/libraries-jaxrs-access-log.json:s1`