**結論**: RESTfulウェブサービスでは、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）がエラー処理の中心で、`ErrorResponseBuilder`がエラーレスポンス生成を、`JaxRsErrorLogWriter`がログ出力を担う。未捕捉例外の最終防衛は`GlobalErrorHandler`（グローバルエラーハンドラ）が担当する。

**根拠**:

**① JaxRsResponseHandler — エラーレスポンス生成とログ出力の主担当**

後続のリソース（アクション）クラスやリクエストボディ変換ハンドラで例外が発生すると、このハンドラがキャッチしてレスポンスを構築する。

- **レスポンス生成**: `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` が処理する。例外クラスが `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の結果がそのままクライアントに返る
- **ログ出力**: `errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` が処理する

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

両プロパティを省略すると各デフォルト実装が使用される。プロジェクト要件を満たせない場合はデフォルト実装クラスを継承して対応する。

**② ErrorResponseBuilder のカスタマイズ例**

バリデーションエラー時にJSONボディを返す例：

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

特定例外に個別ステータスコードを返す場合：

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

**③ GlobalErrorHandler — 未捕捉例外の最終処理**

ハンドラキューの先頭付近に配置し、`JaxRsResponseHandler` より上流でも発生しうる未捕捉例外を捕捉する。例外・エラーの種類に応じたログレベルで出力する：

| 例外/エラー | ログレベル・処理 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` 呼び出し（レベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力し `Result.Error` を返却 |
| その他の例外 | FATALレベルでログ出力し `InternalError` を返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルでログ出力し `InternalError` を返却 |

**④ 障害ログの出力方針**

障害ログは2種類あり、それぞれ専用ロガー（`MONITOR`）とアプリケーションログに分けて出力する：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール連携用） | FATAL、ERROR | `MONITOR` |
| 障害解析ログ（詳細解析用） | FATAL、ERROR | クラス名 |

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ時に例外が発生すると、フレームワークはWARNレベルでログ出力後、ステータスコード500を返す
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること。これより手前で例外が発生した場合はアプリケーションサーバやJVMに処理が委ねられる

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, libraries-failure-log.json:s1