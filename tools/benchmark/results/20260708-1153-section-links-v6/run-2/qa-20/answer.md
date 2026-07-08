**結論**: RESTfulウェブサービスのエラー処理は、ハンドラキューに配置された「グローバルエラーハンドラ」と「Jakarta RESTful Web Servicesレスポンスハンドラ」の2つが協調して担当する。前者が未捕捉例外のログ出力を、後者がエラーレスポンスの生成とログ出力を行う。

**根拠**:

**ハンドラの役割分担（最小ハンドラ構成上の位置）**

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーの場合、ログ出力を行う |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外(エラー)に対応したレスポンスの生成・書き込み・ログ出力処理を行う |

---

**① Jakarta RESTful Web Servicesレスポンスハンドラ（JaxRsResponseHandler）**

エラーレスポンス生成は `errorResponseBuilder` プロパティの `ErrorResponseBuilder` が担当し、ログ出力は `errorLogWriter` プロパティの `JaxRsErrorLogWriter` が担当する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <!-- エラーレスポンス生成をカスタマイズする場合 -->
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
  <!-- エラーログ出力をカスタマイズする場合 -->
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

なお、発生した例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` が返す `HttpResponse` がそのままクライアントに返される（`ErrorResponseBuilder` は呼ばれない）。

設定を省略した場合はデフォルト実装が使用される。カスタマイズが必要な場合はデフォルト実装クラスを継承して対応する。

**エラーレスポンスのカスタマイズ例（バリデーションエラー時にJSONメッセージを返す場合）**

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

---

**② グローバルエラーハンドラ（GlobalErrorHandler）**

未捕捉の例外・エラーをキャッチし、例外の種類に応じてログを出力する。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出し、ログ出力（ログレベルは実装クラスにより異なる） |
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力 |
| 上記以外の例外 | FATALレベルのログ出力後、`InternalError` を生成して返却 |

エラーについてはStackOverflowError・OutOfMemoryErrorなどもFATALレベルで出力される（ThreadDeathのみINFO）。

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ処理中に例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを自動生成する。カスタマイズ時は処理中に例外が発生しないよう実装すること。
- グローバルエラーハンドラは設定による実装切り替えができない。ログレベルを細かく制御したい場合はプロジェクト固有のエラー処理ハンドラを別途作成すること。

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
  RESTfulウェブサービスで使用するハンドラ
  最小ハンドラ構成