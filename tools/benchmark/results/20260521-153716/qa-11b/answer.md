これで必要なセクションの内容はすべて取得できました。回答を生成します。

---

**結論**: RESTfulウェブサービスでは、エラー処理は主に **`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）** と **`GlobalErrorHandler`（グローバルエラーハンドラ）** の2つのハンドラが担う。前者がエラーレスポンスの生成とログ出力を行い、後者が未捕捉例外・エラーを最終的に捕捉してログを出力する。

---

**根拠**:

### ハンドラキューにおける役割分担

最小ハンドラ構成でのエラー処理の流れ：

| No. | ハンドラ | エラー時の処理 |
|-----|--------|------------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力（最終安全網） |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・ログ出力 |

---

### JaxRsResponseHandler の動作

**レスポンスの生成**は `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が行う。

- 発生した例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` が返す `HttpResponse` をそのままクライアントに返す
- それ以外はデフォルト実装の `ErrorResponseBuilder` が処理する
- 設定例：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ログ出力**は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が行う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

どちらも省略時はデフォルト実装が使われる。

---

### GlobalErrorHandler の動作

後続ハンドラで発生した**未捕捉の例外・エラー**を捕捉し、例外の種類に応じてログを出力する：

| 例外クラス | 処理内容 |
|-----------|--------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力。ログレベルは実装クラスによる |
| `Result.Error`（サブクラス含む） | FATALレベルのログを出力し、`Result.Error` を結果として返却 |
| 上記以外の例外 | FATALレベルのログを出力し、`InternalError` を生成して返却 |
| `OutOfMemoryError` | FATALログ出力前に標準エラー出力にも出力（ログ出力自体が失敗する可能性があるため） |

このハンドラは**できるだけハンドラキューの先頭に配置**すること。

---

### カスタマイズ例

バリデーションエラー時にJSON形式でエラーメッセージをレスポンスに含めたい場合は `ErrorResponseBuilder` を継承する：

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
        return response;
    }
}
```

特定の例外に個別のステータスコードを返したい場合も同様：

```java
@Override
public HttpResponse build(final HttpRequest request,
        final ExecutionContext context, final Throwable throwable) {
    if (throwable instanceof NoDataException) {
        return new HttpResponse(404);
    } else {
        return super.build(request, context, throwable);
    }
}
```

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して処理を継続する。カスタム実装では例外が発生しないよう注意すること。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, restful-web-service-architecture.json:s4, handlers-global-error-handler.json:s4

---