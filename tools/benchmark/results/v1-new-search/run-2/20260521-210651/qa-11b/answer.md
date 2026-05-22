これで十分な情報が得られました。Step 5〜8を実行します。

---

## Step 5〜7: 回答生成・検証

**結論**: RESTfulウェブサービスでは「エラー画面」ではなく「エラーレスポンス（HTTPステータスコード + ボディ）」を返す仕組みであり、エラー処理は主に **Jakarta RESTful Web Servicesレスポンスハンドラ**（`JaxRsResponseHandler`）と **グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担当する。

**根拠**:

### ハンドラキューにおける役割分担

最小ハンドラ構成では、以下の順序で配置される。

| No. | ハンドラ | エラー時の役割 |
|-----|---------|--------------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーをキャッチしてログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | エラーレスポンスの生成・書き込みとログ出力 |

---

### Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）

#### エラーレスポンスの生成

エラーレスポンスの生成は `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が行う。

- 発生した例外が `HttpErrorResponse` の場合: `HttpErrorResponse#getResponse()` の戻り値をそのまま返す
- それ以外: デフォルト実装（または独自実装）の `ErrorResponseBuilder` が生成

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

例として、`ApplicationException`（バリデーションエラー）時に JSON のエラーメッセージを返す実装:

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

特定の例外に対して個別のステータスコードを返す場合も同様に `ErrorResponseBuilder` を継承して実装する:

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

#### エラーログの出力

エラーログの出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が行う。設定を省略した場合はデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### グローバルエラーハンドラ（`GlobalErrorHandler`）

ハンドラキューの先頭（できるだけ）に配置し、後続ハンドラで発生した未捕捉の例外・エラーをキャッチしてログ出力を行う。

| 例外クラス | 処理内容 |
|-----------|---------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog()` を呼び出す（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATAL レベルでログ出力 |
| その他の例外 | FATAL レベルでログ出力 |

| エラークラス | 処理内容 |
|------------|---------|
| `ThreadDeath` | INFO レベルでログ出力後、リスロー |
| `StackOverflowError` | FATAL レベルでログ出力 |
| `OutOfMemoryError` | 標準エラー出力後に FATAL レベルでログ出力 |
| `VirtualMachineError`（上記以外） | FATAL レベルでログ出力後、リスロー |
| その他のエラー | FATAL レベルでログ出力 |

---

### HTTPアクセスログ

リクエスト開始時・終了時のログは、`HTTPアクセスログ（RESTfulウェブサービス用）ハンドラ` を追加することで出力できる。ロガー名 `HTTP_ACCESS`、ログレベル `INFO` で出力される。

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはその例外を WARN レベルでログ出力し、ステータスコード 500 のレスポンスを生成して処理を継続する。`ErrorResponseBuilder` をカスタマイズする場合は、処理中に例外が発生しないよう実装すること。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4, libraries-jaxrs-access-log.json:s1

---