**結論**: Nablarch 6では、エラー発生時のエラー画面表示は主に**HttpErrorHandler**（ウェブ用）と**GlobalErrorHandler**（共通）が担い、ログ出力は**障害ログ機能**（`FailureLogUtil`）と**ログ機能**（`Logger`/`LoggerManager`）の組み合わせで実現します。

**根拠**:

### エラー画面の表示（ウェブアプリケーション）

`HttpErrorHandler` が例外の種類に応じてHTTPレスポンスを生成し、エラーページへ遷移させます。

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外 | FATAL | 500 |

エラーページはコンポーネント設定ファイルで `defaultPages` プロパティに正規表現で指定できます：

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="404" value="/NOT_FOUND.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
    </map>
  </property>
</component>
```

システム全体で共通のエラーページに遷移させたい場合は、独自のエラー転送ハンドラを作成する方法も推奨されています：

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  public Object handle(Object data, ExecutionContext context) {
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    } catch (OptimisticLockException e) {
      throw new HttpErrorResponse(400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
    }
  }
}
```

### ログ出力の仕組み

**グローバルエラーハンドラ**（`GlobalErrorHandler`）が例外・エラーの種類に応じてログを出力します：

| 例外/エラー | 処理内容 |
|---|---|
| `ServiceError` | `ServiceError#writeLog` を呼び出し（レベルは実装クラスによる） |
| `Result.Error` | FATALレベルのログを出力 |
| `StackOverflowError` | FATALレベル（標準エラー出力にも出力） |
| `OutOfMemoryError` | FATAL（先に標準エラー出力へ出力） |
| 上記以外の例外 | FATALレベルのログを出力 |

**障害ログ**は2種類あります：

| 種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | 監視ツールによる障害検知 |
| 障害解析ログ | FATAL/ERROR | クラス名 | 障害原因の調査 |

アプリケーションコードからの障害ログ出力には `FailureLogUtil` を使います：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

バッチ・メッセージングでは例外をハンドラに委譲する方法も使えます：

```java
throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
// または
throw new ProcessAbnormalEnd(100, e, "USER_NOT_FOUND");
```

**通常ログ**は `Logger`/`LoggerManager` で出力します：

```java
private static final Logger LOGGER = LoggerManager.get(UserManager.class);

if (LOGGER.isDebugEnabled()) {
    LOGGER.logDebug("userId[" + user.getId() + "]");
}
```

ログ設定は `log.properties` に記述します（`LoggerFactory`、`LogWriter`、ロガー設定の3要素で構成）。

**注意点**:
- `Result.Error` のログ出力可否は `writeFailureLogPattern` プロパティで制御します。このプロパティに設定した正規表現が `Error#getStatusCode()` にマッチした場合のみFATALログを出力します
- `ThreadDeath` および `VirtualMachineError`（`StackOverflowError`・`OutOfMemoryError` 以外）は `GlobalErrorHandler` ではリスローされます（ログ出力後）
- 障害ログの `$data$`（処理対象データ）にはセキュリティ要件に応じて個人情報・機密情報を除外するカスタマイズが必要な場合があります
- `log.properties` の `availableLoggersNamesOrder` は記述順が重要で、より限定的な正規表現のロガー設定を先に記述してください

参照:
- `component/handlers/handlers-HttpErrorHandler.json#s4`
- `component/handlers/handlers-HttpErrorHandler.json#s5`
- `component/handlers/handlers-HttpErrorHandler.json#s6`
- `component/handlers/handlers-global-error-handler.json#s4`
- `component/libraries/libraries-failure-log.json#s1`
- `component/libraries/libraries-failure-log.json#s3`
- `component/libraries/libraries-failure-log.json#s4`
- `component/libraries/libraries-log.json#s6`
- `component/libraries/libraries-log.json#s7`
- `processing-pattern/web-application/web-application-forward-error-page.json#s1`