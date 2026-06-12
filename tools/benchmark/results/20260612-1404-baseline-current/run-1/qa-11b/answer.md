**結論**: RESTfulウェブサービスのエラー処理は、主に**Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）**と**グローバルエラーハンドラ（`GlobalErrorHandler`）**の2層構造で行われます。エラーレスポンスの生成は `ErrorResponseBuilder`、エラーログの出力は `JaxRsErrorLogWriter` が担当します。

---

**根拠**:

### ハンドラの役割分担（最小ハンドラ構成）

| No. | ハンドラ | 例外処理 |
|-----|---------|---------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・ログ出力 |

---

### 1. `JaxRsResponseHandler` によるエラーレスポンス生成

後続ハンドラで発生した例外のレスポンスは `errorResponseBuilder` プロパティの `ErrorResponseBuilder` が生成します。

- 例外が `HttpErrorResponse` の場合 → `HttpErrorResponse#getResponse()` の結果をそのままクライアントに返す
- それ以外 → デフォルトの `ErrorResponseBuilder` でレスポンスを生成

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

特定の例外に対して個別のステータスコードを返す場合は `ErrorResponseBuilder` を継承して実装します：

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

バリデーションエラー時にレスポンスボディにメッセージを設定する場合も同様に `ErrorResponseBuilder` を拡張します。

---

### 2. `JaxRsResponseHandler` によるエラーログ出力

エラーログは `errorLogWriter` プロパティの `JaxRsErrorLogWriter` が担当します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

プロジェクト要件を満たせない場合は `JaxRsErrorLogWriter` を継承してカスタマイズします。

---

### 3. `GlobalErrorHandler` による未捕捉例外の処理

ハンドラキューの最先頭に配置し、未捕捉の例外・エラーを捕捉してログを出力します。

| 例外クラス | 処理内容 |
|-----------|---------|
| `ServiceError`（サブクラス含む） | `writeLog` を呼び出しログ出力（レベルはサブクラス依存）|
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力 |
| 上記以外の例外 | FATALレベルのログ出力 → `InternalError` を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルのログ出力 → `InternalError` を返却 |
| `VirtualMachineError`（上記2つ以外） | FATALレベルのログ出力 → リスロー |

---

### 4. HTTPアクセスログ（リクエスト証跡）

アクセスログは `JaxRsAccessLogHandler` を使用して出力します。INFOレベルで `HTTP_ACCESS` ロガーに出力されます。

```properties
# HTTPアクセスログの設定
loggers.ACC.nameRegex=HTTP_ACCESS
loggers.ACC.level=INFO
loggers.ACC.writerNames=appLog
```

リクエスト処理開始・終了のログをそれぞれ出力し、URLやステータスコード、処理時間などが記録されます。

---

**注意点**:
- `ErrorResponseBuilder` をカスタマイズする場合、そのクラス内で例外が発生するとレスポンスが返せなくなります。カスタマイズ時は例外が発生しないよう実装してください。その場合フレームワークはWARNレベルでログ出力し、ステータスコード500を返します。
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置してください。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, restful-web-service-architecture.json:s4, libraries-jaxrs-access-log.json:s1