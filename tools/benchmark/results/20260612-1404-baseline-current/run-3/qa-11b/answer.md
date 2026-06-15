**結論**: RESTfulウェブサービスのエラー処理は、ハンドラキューに配置された「グローバルエラーハンドラ」と「Jakarta RESTful Web Servicesレスポンスハンドラ」の2層構造で行われる。エラー画面（JSP等）は表示せず、エラー内容はHTTPレスポンス（JSONなど）として返却され、ログはそれぞれのハンドラが担当する。

---

**根拠**:

#### ハンドラキューの全体像

最小ハンドラ構成における例外処理の担当は次のとおり。

| No. | ハンドラ | 例外処理 |
|-----|---------|---------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・書き込み・ログ出力 |

---

#### Jakarta RESTful Web Servicesレスポンスハンドラの仕組み

**レスポンス生成**: `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` が担当する。

- 発生した例外が `HttpErrorResponse` の場合 → `HttpErrorResponse#getResponse()` の戻り値をそのままクライアントに返す
- それ以外の例外 → `ErrorResponseBuilder` がレスポンスを生成する（デフォルト実装あり）
- `ErrorResponseBuilder` の処理中に例外が発生した場合 → WARNレベルのログを出力し、ステータスコード500のレスポンスを返す

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ログ出力**: `errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` が担当する。省略時はデフォルト実装が使用され、要件を満たせない場合はデフォルト実装クラスを継承してカスタマイズする。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

#### グローバルエラーハンドラの仕組み

捕捉した例外・エラーの種別に応じて次の処理を行う。

**例外の処理内容**:

| 例外クラス | 処理内容 |
|---------|---------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力後、`ServiceError` を返却 |
| `Result.Error`（サブクラス含む） | FATALレベルのログを出力後、`Result.Error` を返却 |
| 上記以外の例外 | FATALレベルのログを出力後、`InternalError` を生成して返却 |

**エラーの処理内容**:

| エラークラス | 処理内容 |
|---------|---------|
| `ThreadDeath` | INFOレベルのログを出力後、リスロー |
| `StackOverflowError` | FATALレベルのログを出力後、`InternalError` を返却 |
| `OutOfMemoryError` | 標準エラー出力に出力後、FATALレベルのログを出力し、`InternalError` を返却 |
| `VirtualMachineError`（上記2つ除く） | FATALレベルのログを出力後、リスロー |
| 上記以外のエラー | FATALレベルのログを出力後、`InternalError` を返却 |

---

#### カスタマイズ方法

**バリデーションエラー時にJSON形式のエラーメッセージをレスポンスに含める**場合は `ErrorResponseBuilder` を継承して実装する。

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
    // ...
}
```

**特定の例外に対して個別のステータスコードを返す**（例: `NoDataException` → 404）場合も同様に `ErrorResponseBuilder` を継承する。

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

**注意点**:
- グローバルエラーハンドラは設定による実装切り替えができない。ログレベルの細かな制御など要件を満たせない場合はプロジェクト固有のエラー処理ハンドラを新たに作成すること。
- `ErrorResponseBuilder` の実装中に例外を発生させないよう注意すること。例外が発生するとWARNログのみ出力され、問答無用でステータスコード500が返される。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4