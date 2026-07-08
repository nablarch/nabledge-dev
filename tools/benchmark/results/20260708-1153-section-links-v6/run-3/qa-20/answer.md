**結論**: RESTfulウェブサービスでのエラー処理は、**Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）** がエラーレスポンスとログ出力を担い、その外側の **グローバルエラーハンドラ（`GlobalErrorHandler`）** が未捕捉の実行時例外・エラーのFATALログ出力を担う2層構造になっています。

**根拠**:

**ハンドラキューの役割分担（最小ハンドラ構成より）**

| No. | ハンドラ | エラー時の動作 |
|-----|---------|--------------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | **Jakarta RESTful Web Servicesレスポンスハンドラ** | 例外に対応したレスポンス生成＋ログ出力 |

**① JaxRsResponseHandler — レスポンス生成とログ出力**

エラーレスポンスの生成は `errorResponseBuilder` プロパティの `ErrorResponseBuilder` が行います。例外クラスが `HttpErrorResponse` の場合はそのまま `HttpResponse` を返します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

ログ出力は `errorLogWriter` プロパティの `JaxRsErrorLogWriter` が行います。どちらも省略するとデフォルト実装が使われます。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

**② エラー時のレスポンスをカスタマイズする（拡張例）**

バリデーションエラー時にエラーメッセージをJSONで返す場合：

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

特定の例外に個別のステータスコードを返す場合：

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

**③ GlobalErrorHandler — 最終的な未捕捉例外の処理**

例外の種類に応じたログレベル：

| 例外クラス | ログレベル |
|-----------|-----------|
| `ServiceError`（サブクラス含む） | `ServiceError` の実装クラスにより異なる |
| `Result.Error`（サブクラス含む） | FATAL |
| 上記以外の例外 | FATAL |
| `OutOfMemoryError` | FATAL（標準エラー出力にも出力） |

**注意点**:
- `GlobalErrorHandler` はハンドラキューの先頭（できるだけ最前列）に配置すること。これより手前のハンドラで例外が発生した場合、ウェブアプリケーションサーバやJVMにより処理される。
- `ErrorResponseBuilder` のカスタマイズ時は、処理中に例外が発生しないように実装すること。例外が発生するとWARNログが出力されてステータスコード500のレスポンスが返される。

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
  制約
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md
  最小ハンドラ構成