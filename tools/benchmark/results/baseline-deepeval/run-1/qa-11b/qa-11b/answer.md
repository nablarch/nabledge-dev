セクション内容を確認できました。Step 5: 回答を生成します。

**結論**: RESTfulウェブサービスでのエラー処理は、主に **`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）** と **`GlobalErrorHandler`（グローバルエラーハンドラ）** の2つのハンドラが担う。エラー時のHTTPレスポンス生成とログ出力はそれぞれ独立したコンポーネント（`ErrorResponseBuilder` と `JaxRsErrorLogWriter`）が行い、カスタマイズ可能な設計になっている。

**Verify**: 回答に含む主なNablarch固有クレーム：
- `JaxRsResponseHandler` → s4, s5で直接記述 ✅
- `ErrorResponseBuilder` プロパティ → s4で記述 ✅
- `JaxRsErrorLogWriter` プロパティ → s5で記述 ✅
- `HttpErrorResponse` の場合は `getResponse()` から戻る → s4で記述 ✅
- `GlobalErrorHandler`(nablarch.fw.handler.GlobalErrorHandler) → s4の最小ハンドラ構成表 ✅
- `ServiceError`, `Result.Error` の例外別処理 → s4(global error handler)で記述 ✅
- 障害ログのロガー名 `MONITOR` → libraries-failure-log s1で記述 ✅
- `FailureLogUtil.logError` → s3で記述 ✅

**verify_result = PASS**

---

**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキューの前段に配置した **グローバルエラーハンドラ**（`GlobalErrorHandler`）と、その直後の **Jakarta RESTful Web Servicesレスポンスハンドラ**（`JaxRsResponseHandler`）の2つが連携して行う。エラーレスポンスの生成とログ出力はそれぞれ差し替え可能なコンポーネントが担う設計になっている。

**根拠**:

### ハンドラの役割分担（最小ハンドラ構成）

| No. | ハンドラ | エラー時の動作 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | JaxRsResponseHandler | 例外に対応したレスポンス生成＋ログ出力 |

---

### JaxRsResponseHandler — エラーレスポンス生成

エラーレスポンスの生成は `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` が行う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

- 発生例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の値をそのままクライアントに返す
- 設定省略時はデフォルト実装の `ErrorResponseBuilder` が使われる
- `ErrorResponseBuilder` 内で例外が発生した場合、WARNレベルでログを出力しステータスコード500を返す

### JaxRsResponseHandler — エラーログ出力

ログ出力は `errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` が行う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

設定省略時はデフォルト実装が使われ、プロジェクト要件に合わない場合はデフォルト実装クラスを継承してカスタマイズする。

---

### グローバルエラーハンドラ — 例外種別ごとの処理

`GlobalErrorHandler` はハンドラキューの先頭付近に配置し、後続ハンドラの未捕捉例外を捕捉する。

| 例外クラス | ログレベル | 処理内容 |
|---|---|---|
| `ServiceError`（サブクラス含む） | ServiceError実装による | `ServiceError#writeLog` を呼び出す |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後、`Result.Error` を返却 |
| 上記以外の例外 | FATAL | ログ出力後、`InternalError` を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATAL | ログ出力後、`InternalError` を返却 |
| `VirtualMachineError`（上記以外） | FATAL | ログ出力後、リスロー |
| `ThreadDeath` | INFO | ログ出力後、リスロー |

---

### 障害ログの出力方針

フレームワークは障害ログを2種類に分けて出力する。

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL, ERROR | `MONITOR` |
| 障害解析ログ（アプリログ） | FATAL, ERROR | クラス名 |

アプリケーションコードから明示的にログを出力する場合は `FailureLogUtil` を使う（バッチやメッセージングで主に使用）。

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

---

### 拡張例：エラーレスポンスのカスタマイズ

バリデーションエラー時にJSONのエラーメッセージを返したい場合は `ErrorResponseBuilder` を継承する。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            HttpResponse response = new HttpResponse(400);
            response.setContentType(MediaType.APPLICATION_JSON);
            // エラーメッセージをボディに設定
            return response;
        }
        return super.build(request, context, throwable);
    }
}
```

特定例外に個別のステータスコードを返す場合も同様。

```java
if (throwable instanceof NoDataException) {
    return new HttpResponse(404);
}
```

**参照:**
- `handlers-jaxrs-response-handler.json:s4`
- `handlers-jaxrs-response-handler.json:s5`
- `handlers-jaxrs-response-handler.json:s7`
- `handlers-jaxrs-response-handler.json:s8`
- `restful-web-service-architecture.json:s4`
- `handlers-global-error-handler.json:s4`
- `libraries-failure-log.json:s1`

---