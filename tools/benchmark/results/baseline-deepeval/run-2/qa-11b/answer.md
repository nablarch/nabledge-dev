Step 5〜7: 回答を生成して検証します。

---

**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキューに配置された **グローバルエラーハンドラ**（No.1）と **Jakarta RESTful Web Servicesレスポンスハンドラ**（No.2）の2つのハンドラが担う。前者が未捕捉例外のログ出力を、後者がエラーレスポンスの生成とログ出力を行う。

---

**根拠**:

### ハンドラキューにおける役割分担

最小ハンドラ構成でのエラー処理担当：

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外またはエラーの場合、ログ出力を行う |
| 2 | JaxRsResponseHandler | 例外に対応したレスポンスの生成・書き込みとログ出力を行う |

### エラーレスポンスの生成（JaxRsResponseHandler）

`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` がレスポンスを生成する。例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` が使われる。設定を省略するとデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

エラーログの出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

### 例外種別ごとのログ出力（グローバルエラーハンドラ）

グローバルエラーハンドラが捕捉した例外・エラーは次のとおり処理される：

| 例外/エラークラス | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | 実装クラスによる | `ServiceError#writeLog()` を呼び出す |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後 `Result.Error` を返却 |
| `ThreadDeath`（サブクラス含む） | INFO | ログ出力後リスロー |
| `StackOverflowError` / `OutOfMemoryError` | FATAL | ログ出力後 `InternalError` を生成して返却 |
| 上記以外の例外・エラー | FATAL | ログ出力後 `InternalError` を生成して返却 |

### 障害ログの出力方針

障害ログは2種類に分かれる：

| 種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | 監視専用ファイル（monitor.log 等） |
| 障害解析ログ | FATAL/ERROR | クラス名 | アプリケーションログ（app.log 等） |

アプリコードから明示的に障害ログを出力したい場合は `FailureLogUtil` を使う：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- グローバルエラーハンドラは **ハンドラキューの先頭** に配置すること。これより手前のハンドラで例外が発生した場合、アプリケーションサーバまたはJVMによる例外処理になる。
- `ErrorResponseBuilder` をカスタマイズする場合、**その処理中に例外が発生しないよう実装すること**。処理中に例外が発生した場合、フレームワークはWARNレベルでログを出力しステータスコード500のレスポンスを返す。

---

参照:
- `handlers-jaxrs-response-handler.json:s4`
- `handlers-jaxrs-response-handler.json:s5`
- `handlers-global-error-handler.json:s4`
- `restful-web-service-architecture.json:s4`
- `libraries-failure-log.json:s1`
- `libraries-failure-log.json:s3`

---