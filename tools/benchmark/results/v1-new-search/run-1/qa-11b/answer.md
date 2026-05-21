Step 5-7: 回答を生成し検証します。

**結論**: RESTfulウェブサービスのエラー処理は、ハンドラキュー内の「Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）」と「グローバルエラーハンドラ（`GlobalErrorHandler`）」の2段構えで行われる。前者がREST用のエラーレスポンス生成とログ出力を担い、後者が最終的な未捕捉例外のログ出力を担う。

**根拠**:

### 最小ハンドラ構成におけるエラー処理の役割分担

最小ハンドラ構成（ハンドラキューの順番）でのエラー関連ハンドラ：

| No. | ハンドラ | 例外処理 |
|-----|----------|----------|
| 1 | グローバルエラーハンドラ | 実行時例外またはエラーの場合、ログ出力を行う |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外(エラー)に対応したレスポンスの生成・書き込み・ログ出力処理 |

---

### Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）

**エラーレスポンスの生成**（`errorResponseBuilder` プロパティ）

- `ErrorResponseBuilder` によってレスポンスが生成される（デフォルト実装あり）
- 例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返される
- カスタマイズする場合は `ErrorResponseBuilder` を継承して設定：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**エラーログ出力**（`errorLogWriter` プロパティ）

- `JaxRsErrorLogWriter` によってログが出力される（デフォルト実装あり）
- カスタマイズする場合は `JaxRsErrorLogWriter` を継承して設定：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### グローバルエラーハンドラ（`GlobalErrorHandler`）

`JaxRsResponseHandler` よりも手前（ハンドラキューの先頭側）に配置され、未捕捉の例外・エラーを最終的に捕捉してログを出力する。

**例外の種類に応じたログレベル：**

| 例外クラス | 処理内容 |
|-----------|---------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog()` を呼び出す（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| 上記以外の例外 | FATALレベルでログ出力後、`InternalError` を生成して返却 |

**エラーの種類に応じた処理：**

| エラークラス | 処理内容 |
|------------|---------|
| `ThreadDeath` | INFOレベルでログ出力後、リスロー |
| `StackOverflowError` | FATALレベルでログ出力後、`InternalError` を返却 |
| `OutOfMemoryError` | 標準エラー出力へ出力後、FATALレベルでログ出力、`InternalError` を返却 |
| `VirtualMachineError`（上記以外） | FATALレベルでログ出力後、リスロー |
| 上記以外のエラー | FATALレベルでログ出力後、`InternalError` を返却 |

---

### アクセスログ（HTTPアクセスログ）

`JaxRsAccessLogHandler` を使用すると、リクエスト開始・終了時のアクセスログが出力される。ログレベルはINFO、ロガー名は `HTTP_ACCESS`。

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ中に例外が発生すると、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを生成して継続する。そのため、`ErrorResponseBuilder` の実装では例外が発生しないように注意が必要。
- グローバルエラーハンドラはできるだけハンドラキューの先頭に配置すること。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-global-error-handler.json:s4, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, libraries-jaxrs-access-log.json:s1

---