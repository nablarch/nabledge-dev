**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキューの先頭2つのハンドラが分担する。**グローバルエラーハンドラ**が実行時例外・エラーのログ出力を担い、**Jakarta RESTful Web Servicesレスポンスハンドラ**がエラーレスポンスの生成・書き込みとログ出力を担う。

---

**根拠**:

### ハンドラ構成と役割分担

最小ハンドラ構成（ハンドラキューの先頭2件）での例外処理の役割：

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーの場合、ログ出力を行う |
| 2 | JaxRsResponseハンドラ | 例外に対応したレスポンスの生成・書き込みとログ出力を行う |

---

### グローバルエラーハンドラのログ出力

捕捉した例外・エラーの種類に応じてログレベルが変わる：

| 例外/エラークラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出す（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| `ThreadDeath` | INFOレベルでログ出力後リスロー |
| `StackOverflowError` / `OutOfMemoryError` / `VirtualMachineError` | FATALレベルでログ出力 |
| 上記以外の例外・エラー | FATALレベルでログ出力 |

---

### JaxRsResponseハンドラのエラーレスポンス生成

エラーレスポンスの生成は `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が担う。

- 発生した例外が `HttpErrorResponse` の場合 → `HttpErrorResponse#getResponse()` の戻り値をクライアントに返す
- それ以外 → `ErrorResponseBuilder` がレスポンスを生成する（デフォルト実装あり、継承してカスタマイズ可能）

バリデーションエラー時にJSONメッセージを返す例：
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
}
```

特定例外に個別ステータスコードを返す例（`NoDataException` → 404）：
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

### JaxRsResponseハンドラのエラーログ出力

エラーログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う（デフォルト実装あり、継承してカスタマイズ可能）。

---

### フレームワーク全体のログ出力方針

| ログレベル | 出力方針 |
|---|---|
| FATAL/ERROR | 障害ログ。1件の障害に対して1件出力する方針 |
| WARN | 障害ログとして出力できない連鎖例外（例：業務処理とトランザクション終了の両方で例外が発生した場合の後者） |
| INFO | URLパラメータ改竄エラー・認可チェックエラーなど |

障害ログには2種類あり、用途別にロガー名が分かれている：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL/ERROR | `MONITOR` |
| 障害解析ログ（アプリログ向け） | FATAL/ERROR | クラス名 |

---

### アクセスログ

HTTPアクセスログはINFOレベルで `HTTP_ACCESS` ロガー名で出力され、アプリケーションログに記録される。

---

**注意点**:

- `ErrorResponseBuilder` の処理中に例外が発生すると、WARNレベルでログが出力されてステータスコード500のレスポンスが返される。カスタマイズ時は `ErrorResponseBuilder` 内で例外が発生しないよう実装すること。
- グローバルエラーハンドラはハンドラキューの先頭に配置する必要がある。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, libraries-failure-log.json:s1, libraries-log.json:s27, libraries-jaxrs-access-log.json:s1, restful-web-service-architecture.json:s4

---