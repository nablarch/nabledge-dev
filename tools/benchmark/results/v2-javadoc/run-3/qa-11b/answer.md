Step 5の回答生成と検証を行います。

**結論**: RESTfulウェブサービスでのエラー処理は、`JaxRsResponseHandler`（エラーレスポンス生成・ログ出力）と`GlobalErrorHandler`（未捕捉例外のFATALログ）の2つのハンドラが連携して行います。

**根拠**:

**ハンドラキューの役割分担（最小構成）**

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | JaxRsResponseHandler | エラーレスポンス生成・ログ出力 |
| 3以降 | DB・トランザクション・ルーティング等 | — |

---

**① エラーレスポンスの生成（JaxRsResponseHandler）**

後続ハンドラで発生した例外は `JaxRsResponseHandler` の `errorResponseBuilder`（`ErrorResponseBuilder`）が処理します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

- `HttpErrorResponse` が発生した場合は、その `getResponse()` が直接クライアントに返される
- それ以外はデフォルトの `ErrorResponseBuilder` が処理し、プロジェクト要件を満たせない場合はサブクラスで対応

**バリデーションエラー時にJSONメッセージを返す例**:

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

**特定例外に個別ステータスコードを返す例**:

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

**② エラー時のログ出力（JaxRsResponseHandler）**

エラーログは `JaxRsResponseHandler` の `errorLogWriter`（`JaxRsErrorLogWriter`）が担当します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

デフォルト実装で要件を満たせない場合はサブクラスで対応します。

---

**③ 致命的エラーのログ出力（グローバルエラーハンドラ）**

`JaxRsResponseHandler` より外側に配置される `GlobalErrorHandler` は、未捕捉の例外・エラーを捕捉してログを出力します。

| 例外クラス | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError` の実装クラスに依存 |
| `Result.Error`（サブクラス含む） | FATAL |
| 上記以外の例外・エラー | FATAL |

---

**④ アクセスログ（JaxRsAccessLogHandler）**

`JaxRsAccessLogHandler` はリクエスト開始・終了時のアクセスログを出力します（ロガー名: `HTTP_ACCESS`、レベル: INFO）。

```properties
jaxRsAccessLogFormatter.beginFormat=@@@@ BEGIN @@@@ rid = [$requestId$] uid = [$userId$] ...
jaxRsAccessLogFormatter.endFormat=@@@@ END @@@@ ... status_code = [$statusCode$] ...
```

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装内で例外が発生すると、レスポンスが生成されない。実装時は例外が発生しないよう注意すること。その場合フレームワークはWARNレベルでログ出力し、ステータスコード500を返す。
- `GlobalErrorHandler` はハンドラキューの**先頭**に配置すること。前段で例外が発生した場合はアプリケーションサーバやJVMが処理する。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4, libraries-jaxrs-access-log.json:s1

---