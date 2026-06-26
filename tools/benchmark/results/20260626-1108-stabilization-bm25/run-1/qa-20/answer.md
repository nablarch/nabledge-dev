**結論**: RESTfulウェブサービスでのエラー処理は、`JaxRsResponseHandler` に設定された **`ErrorResponseBuilder`**（エラーレスポンス生成）と **`JaxRsErrorLogWriter`**（エラーログ出力）の2つのコンポーネントが担います。また、Nablarchのログ機能として障害通知ログ・障害解析ログが別途提供されており、`app-log.properties` で設定します。

---

**根拠**:

**1. エラーレスポンスの生成 — `ErrorResponseBuilder`**

例外発生時のレスポンス生成は、`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が行います。例外が `HttpErrorResponse` の場合は、`HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返されます。設定を省略した場合はデフォルト実装が使用されます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

デフォルト実装でプロジェクト要件を満たせない場合は継承クラスを作成します。例えば、`NoDataException` 発生時に404を返す例：

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

**2. エラーログの出力 — `JaxRsErrorLogWriter`**

エラー発生時のログ出力は、`JaxRsResponseHandler` の `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が行います。設定を省略した場合はデフォルト実装が使用されます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

**3. 障害ログ — `FailureLogFormatter`**

フレームワーク全体の障害ログ機能として、障害通知ログ（1次切り分け用）と障害解析ログ（原因特定用）が提供されます。`app-log.properties` で設定します。

```properties
failureLogFormatter.defaultFailureCode=UNEXPECTED_ERROR
failureLogFormatter.defaultMessage=an unexpected exception occurred.
failureLogFormatter.notificationFormat=fail_code = [$failureCode$] $message$
failureLogFormatter.analysisFormat=fail_code = [$failureCode$] $message$
```

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生すると、フレームワークはその例外をWARNレベルでログ出力してステータスコード500のレスポンスを生成します。`ErrorResponseBuilder` 内では例外が発生しないよう実装してください。

参照: `handlers-jaxrs-response-handler.json:s4`, `handlers-jaxrs-response-handler.json:s5`, `handlers-jaxrs-response-handler.json:s7`, `handlers-jaxrs-response-handler.json:s8`, `libraries-failure-log.json:s4`, `libraries-log.json:s3`