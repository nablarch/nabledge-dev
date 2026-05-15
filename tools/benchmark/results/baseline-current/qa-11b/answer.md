**結論**: RESTfulウェブサービスでのエラーレスポンスは `JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）が担い、ログ出力は `JaxRsAccessLogHandler`（アクセスログ）と `GlobalErrorHandler`（グローバルエラーハンドラ）が組み合わさって行われます。

**根拠**:

### 1. エラーレスポンスの生成 — `JaxRsResponseHandler`

後続ハンドラ（リソースクラス等）で例外・エラーが発生すると、`JaxRsResponseHandler` がレスポンスを構築してクライアントに返します。

**クラス名**: `nablarch.fw.jaxrs.JaxRsResponseHandler`

**仕組み**:
- `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` がレスポンスを生成します。
- 省略時はデフォルト実装が使われます。
- 発生例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントへ返ります。

**バリデーションエラー時にエラーメッセージをJSONで返す例**:
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

    private HttpResponse createResponseBody(ApplicationException ae) {
        HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        // エラーメッセージのJSON生成...
        return response;
    }
}
```

**特定例外に対して個別ステータスコードを返す例**:
```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        }
        return super.build(request, context, throwable);
    }
}
```

**設定例**:
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

### 2. エラー時のログ出力 — `JaxRsResponseHandler` の `errorLogWriter`

例外・エラー発生時のログ出力は、`errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` が行います。省略時はデフォルト実装が使われます。プロジェクト要件を満たせない場合はデフォルト実装クラスを継承して対応します。

### 3. 未捕捉例外のログ出力 — `GlobalErrorHandler`

**クラス名**: `nablarch.fw.handler.GlobalErrorHandler`

ハンドラキューの先頭付近に配置し、後続ハンドラの未捕捉例外・エラーを捕捉してログを出力します。

| 例外クラス | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | ServiceErrorの実装クラスによる | `ServiceError#writeLog` を呼び出す |
| `Result.Error`（サブクラス含む） | FATAL | FATALログ出力後、`Result.Error` を返却 |
| 上記以外の例外 | FATAL | FATALログ出力後、`InternalError` を生成して返却 |
| `OutOfMemoryError` | FATAL | 標準エラー出力にも出力（OOMで再失敗しうるため） |

### 4. アクセスログ — `JaxRsAccessLogHandler`

**クラス名**: `nablarch.fw.jaxrs.JaxRsAccessLogHandler`

リクエスト開始時・完了時にアクセスログを出力します。ログレベルは `INFO`、ロガー名は `HTTP_ACCESS`。

```properties
jaxRsAccessLogFormatter.beginFormat=@@@@ BEGIN @@@@ rid = [$requestId$] uid = [$userId$] sid = [$sessionId$]\
    \n\turl = [$url$$query$]\n\tmethod = [$method$]
jaxRsAccessLogFormatter.endFormat=@@@@ END @@@@ rid = [$requestId$] ...status_code = [$statusCode$]
```

### 5. 障害ログ — `FailureLogUtil`

フレームワークは処理方式ごとの例外ハンドラで障害ログを自動出力します。アプリケーションコードで明示的に出力する場合は `FailureLogUtil` を使用します。

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

障害ログは2種類あります：
- **障害通知ログ** (FATAL/ERROR、ロガー名 `MONITOR`): 監視ツール向け
- **障害解析ログ** (FATAL/ERROR、クラス名ロガー): スタックトレース付き

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生するとクライアントへレスポンスを返せなくなります。カスタム実装では例外が発生しないよう実装すること（フレームワークはその場合 WARNログを出力してステータスコード 500 を返します）。
- `JaxRsAccessLogHandler` はスレッドコンテキスト変数管理ハンドラより後ろ、かつ `HttpErrorHandler` より前に配置する必要があります。
- `GlobalErrorHandler` は特に理由がない限りハンドラキューの先頭に配置してください。

参照: component/handlers/handlers-jaxrs-response-handler.json#s4, component/handlers/handlers-jaxrs-response-handler.json#s5, component/handlers/handlers-jaxrs-response-handler.json#s7, component/handlers/handlers-jaxrs-response-handler.json#s8, component/handlers/handlers-global-error-handler.json#s4, component/handlers/handlers-jaxrs-access-log-handler.json#s3, component/libraries/libraries-jaxrs-access-log.json#s1, component/libraries/libraries-failure-log.json#s1