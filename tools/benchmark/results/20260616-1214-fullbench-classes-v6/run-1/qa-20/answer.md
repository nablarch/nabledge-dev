**結論**: RESTfulウェブサービスのエラーハンドリングは、**Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）** がエラーレスポンス生成とログ出力を担い、**グローバルエラーハンドラ（`GlobalErrorHandler`）** が未捕捉の例外・エラーをFATALログ出力する2段構成になっている。

**根拠**:

### 最小ハンドラ構成でのエラー処理の位置づけ

| No. | ハンドラ | 例外処理 |
|-----|---------|---------|
| 1 | グローバルエラーハンドラ | 実行時例外またはエラーの場合、ログ出力を行う |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外(エラー)に対応したレスポンス生成・書き込み・ログ出力処理を行う |

---

### Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）

後続ハンドラで例外・エラーが送出された場合、以下の2つの委譲先クラスが処理を行う。

**① レスポンス生成: `ErrorResponseBuilder`**

`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` によりレスポンスが生成される。省略時はデフォルト実装が使用される。なお、送出された例外が `HttpErrorResponse` の場合は、`HttpErrorResponse#getResponse()` が返す `HttpResponse` がそのままクライアントに返却される。

カスタマイズ例（`ApplicationException` 発生時に JSON でエラーメッセージを返す場合）:

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

特定の例外に個別のステータスコードを返す例:

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

設定例:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**② ログ出力: `JaxRsErrorLogWriter`**

`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` によりログが出力される。省略時はデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### グローバルエラーハンドラ（`GlobalErrorHandler`）

後続ハンドラで発生した未捕捉の例外・エラーを捕捉し、例外の種類に応じたログを出力する。

| 例外クラス | 処理内容 |
|-----------|---------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出しログ出力（ログレベルは実装クラスにより異なる） |
| `Result.Error`（サブクラス含む） | FATALレベルのログを出力 |
| 上記以外の例外クラス | FATALレベルのログを出力し、`InternalError` を返却 |

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ中に例外が発生すると、レスポンスを生成できなくなるため、`ErrorResponseBuilder` の処理中は例外が発生しないよう実装すること。なお、`ErrorResponseBuilder` 処理中に例外が発生した場合、フレームワークはWARNレベルのログを出力し、ステータスコード500のレスポンスを生成して処理を継続する
- グローバルエラーハンドラは設定による実装の切り替えができないため、要件に合わない場合（例: ログレベルを細かく切り替えたい）はプロジェクト固有のハンドラを作成すること

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4