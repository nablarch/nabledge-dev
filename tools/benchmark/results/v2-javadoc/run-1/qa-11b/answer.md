Step 5: 回答を生成します。

**結論**: RESTfulウェブサービスでは、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）がエラー処理の中心を担い、`ErrorResponseBuilder`でHTTPレスポンスを生成し、`JaxRsErrorLogWriter`でログを出力します。また、`GlobalErrorHandler`（グローバルエラーハンドラ）がハンドラキューの先頭で未捕捉例外を一括捕捉し、FATALレベルのログを出力します。

**根拠**:

### JaxRsResponseHandler の仕組み

後続ハンドラ（リソースクラスなど）で例外が発生した場合、`JaxRsResponseHandler` が2つのコンポーネントを使って処理します。

**レスポンス生成（ErrorResponseBuilder）**

デフォルト実装の挙動:
| 例外クラス | ステータスコード |
|---|---|
| `ApplicationException` | 400 |
| 上記以外 | 500 |

`HttpErrorResponse` が発生した場合は、`HttpErrorResponse#getResponse()` が返す `HttpResponse` をそのままクライアントに返します。

**ログ出力（JaxRsErrorLogWriter）**

- `ApplicationException`（バリデーションエラー等）: デフォルトでは**ログ出力しない**（`writeApplicationExceptionLog` が何もしない）
- それ以外の例外: `FailureLogUtil` を使って障害ログを出力する

設定例:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### GlobalErrorHandler の役割

ハンドラキューの先頭付近に配置され、未捕捉の例外やエラーを一括処理します:

| 例外/エラークラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` でログ出力（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力 |
| 上記以外の例外 | FATALレベルのログ出力、`InternalError` を返却 |
| `OutOfMemoryError` | 標準エラー出力に出力後、FATALレベルのログ出力 |

### カスタマイズ例

エラーレスポンスのボディにJSONメッセージを含めたい場合:
```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        } else {
            return super.build(request, context, throwable);
        }
    }
    // ...
}
```

特定例外に対して個別のステータスコードを返したい場合:
```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        } else {
            return super.build(request, context, throwable);
        }
    }
}
```

**注意点**: `ErrorResponseBuilder` をカスタマイズする際、その処理中に例外が発生するとレスポンスを返せなくなります。フレームワークはその場合WARNレベルでログ出力を行い、ステータスコード500のレスポンスを生成しますが、カスタム実装内で例外が発生しないよう注意が必要です。

参照: `handlers-jaxrs-response-handler.json:s4`, `handlers-jaxrs-response-handler.json:s5`, `handlers-jaxrs-response-handler.json:s7`, `handlers-jaxrs-response-handler.json:s8`, `handlers-global-error-handler.json:s4`, `javadoc/javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json:s5`, `javadoc/javadoc-nablarch-fw-jaxrs-ErrorResponseBuilder.json:s2`

---