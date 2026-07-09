**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキューに配置された2つのハンドラが担う。`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）が例外の種類に応じたエラーレスポンス生成とログ出力を行い、`GlobalErrorHandler`（グローバルエラーハンドラ）が未捕捉の実行時例外・エラーをFATALレベルでログ出力する。

**根拠**:

**ハンドラキューの配置（最小構成）**

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーの場合、ログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に応じたレスポンス生成・ログ出力 |

**エラーレスポンスの生成（JaxRsResponseHandler）**

エラーレスポンスの生成は、`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が担当する。

- 発生した例外クラスが `HttpErrorResponse` の場合は、`HttpErrorResponse#getResponse()` から戻される `HttpResponse` がクライアントに返される
- それ以外はデフォルト実装の `ErrorResponseBuilder` が使用される（カスタマイズ可能）

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ログ出力（JaxRsResponseHandler）**

ログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担当する。デフォルト実装で要件を満たせない場合は継承クラスを作成する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

**グローバルエラーハンドラのログ出力レベル**

| 例外クラス | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | ServiceErrorの実装クラスにより異なる |
| `Result.Error`（サブクラス含む） | FATAL |
| 上記以外の例外 | FATAL |
| `ThreadDeath`（サブクラス含む） | INFO |
| `StackOverflowError` / `OutOfMemoryError` / その他エラー | FATAL |

**カスタマイズ例：バリデーションエラー時にJSONメッセージを返す**

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

**注意点**: `ErrorResponseBuilder` をカスタマイズする場合、その処理中に例外が発生するとクライアントにレスポンスを返せない状態になる。フレームワークはWARNレベルでログ出力しステータスコード500のレスポンスを生成するが、カスタマイズ実装では例外が発生しないよう実装すること。

参照:
- Jakarta RESTful Web Servicesレスポンスハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md
  例外及びエラーに応じたレスポンスの生成
  例外及びエラーに応じたログ出力
  エラー時のレスポンスにメッセージを設定する
  特定のエラーの場合に個別に定義したエラーレスポンスを返却する
- グローバルエラーハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md
  例外及びエラーに応じた処理内容
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md
  最小ハンドラ構成