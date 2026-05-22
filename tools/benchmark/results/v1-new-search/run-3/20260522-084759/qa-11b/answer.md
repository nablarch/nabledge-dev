Step 5: 答案を生成します。

**結論**: RESTfulウェブサービスでのエラー処理は主に `JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）が担い、`ErrorResponseBuilder` でエラーレスポンスを生成し、`JaxRsErrorLogWriter` でエラーログを出力する。未捕捉例外は `GlobalErrorHandler` がFATALレベルでログ出力する。

**根拠**:

### エラーレスポンスの生成

`JaxRsResponseHandler` が後続ハンドラで発生した例外/エラーを捉え、`ErrorResponseBuilder` でレスポンスを構築する。発生した例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の内容がそのまま返る。

設定例:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

バリデーションエラー時にJSONメッセージを返したい場合は `ErrorResponseBuilder` を継承してカスタマイズする:

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
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        // エラーメッセージの生成処理
        return response;
    }
}
```

### エラーログの出力

`JaxRsResponseHandler` の `errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` が担う。デフォルト実装が使われ、プロジェクト要件を満たせない場合は継承して対応する:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### グローバルエラーハンドラ（未捕捉例外）

`GlobalErrorHandler` がハンドラキューの先頭に配置され、未捕捉の例外/エラーを捕捉する:

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力（ログレベルは実装クラス依存）|
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力し、`Result.Error` を返却 |
| それ以外の例外 | FATALレベルでログ出力し、`InternalError` を生成して返却 |

### アクセスログ

`JaxRsAccessLogHandler` がリクエスト処理の開始時と終了時にINFOレベルで `HTTP_ACCESS` ロガーへアクセスログを出力する。終了時にはステータスコードも含まれる。

### 障害ログの出力方針

障害ログは2種類のロガーへ出力される:

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL、ERROR | MONITOR |
| 障害解析ログ | FATAL、ERROR | クラス名 |

障害通知ログ（`MONITOR`）は監視ツールから検知するための専用ファイルへ、障害解析ログはアプリケーションログへ出力する。

**注意点**: `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはWARNレベルでログ出力しステータスコード500のレスポンスを生成する。カスタマイズ時は `ErrorResponseBuilder` 内で例外が発生しないよう実装すること。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-global-error-handler.json:s4, libraries-jaxrs-access-log.json:s1, libraries-failure-log.json:s1

---