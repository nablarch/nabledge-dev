**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキュー内の2つのハンドラが役割分担しており、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）がエラー応答の生成とログ出力を担い、`GlobalErrorHandler`（グローバルエラーハンドラ）が未捕捉の実行時例外・エラーのログ出力を担う。

**根拠**:

**ハンドラキューの構造（エラー関連の抜粋）**:

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・ログ出力 |

---

**① Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）**

後続のハンドラ（リソースクラス等）で例外が発生した場合に、エラーレスポンスの生成とログ出力を行う中心的なハンドラ。

**レスポンスの生成**: `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が担う。

- 例外が `HttpErrorResponse` の場合: `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返却される
- それ以外の例外: デフォルト実装の `ErrorResponseBuilder` が使用される

カスタマイズが必要な場合は継承クラスを作成する:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

例として `NoDataException` のとき404を返す実装:
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

**ログ出力**: `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う。プロジェクト要件を満たせない場合は継承クラスを作成する:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

**② グローバルエラーハンドラ（`GlobalErrorHandler`）**

`JaxRsResponseHandler` より外側（ハンドラキューの先頭側）に配置し、未捕捉の例外・エラーを捕捉してログ出力する。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` でログ出力。ログレベルは実装クラスにより異なる。 |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| 上記以外の例外 | FATALレベルでログ出力後、`InternalError` を生成して返却 |
| `OutOfMemoryError` | FATALログ出力前に標準エラー出力へ出力（再度OOMが発生する可能性のため） |

**注意点**:

- `ErrorResponseBuilder` のカスタマイズ実装の中で例外が発生した場合、フレームワークはWARNレベルでログ出力してステータスコード500のレスポンスを生成して処理を継続する
- グローバルエラーハンドラはできるだけハンドラキューの先頭に配置すること。このハンドラより手前で例外が発生した場合は、ウェブアプリケーションサーバやJVMにより例外処理が行われる

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4