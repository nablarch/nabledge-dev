**結論**: Nablarchのエラー処理は「ハンドラによる例外捕捉とログ出力」「エラー画面への遷移」「障害ログ機能」の3層で構成されています。

**根拠**:

### 1. エラーハンドラによる例外捕捉とログ出力

**Webアプリケーション: `HttpErrorHandler`**

発生した例外の種類に応じてログレベルとHTTPステータスが自動的に決まります。

| 例外クラス | ログレベル | ステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `getResponse()`の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外 | FATAL | 500 |

`Result.Error` の場合は `writeFailureLogPattern` プロパティ（正規表現）でログ出力有無を制御できます。

**バッチ/メッセージング: グローバルエラーハンドラ**

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError` | `writeLog()` 呼び出し（ログレベルは実装クラスによる） |
| `Result.Error` | FATALログ出力後、結果として返却 |
| `ThreadDeath` | INFOログ出力後、リスロー |
| `OutOfMemoryError` | 標準エラー出力→FATALログ出力後、`InternalError`返却 |
| 上記以外 | FATALログ出力後、`InternalError`返却 |

### 2. エラー画面への遷移

**個別指定**: アクションメソッドに `@OnError` / `@OnErrors` インターセプタでエラー時遷移先を指定。

**システム共通**: 専用のエラーフォワードハンドラを実装してハンドラキューに追加するのが推奨パターンです。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
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

**デフォルトエラーページ**: `HttpErrorHandler` の `defaultPages` でHTTPステータスコードパターン（正規表現）ごとにJSPを設定できます。ただし `web.xml` の `error-page` 要素との重複設定が必要なため、`web.xml` への設定が推奨されています。

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

### 3. 障害ログの出力

`FailureLogUtil` を使って障害コード付きでログを出力します。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

バッチ処理では `TransactionAbnormalEnd` / `ProcessAbnormalEnd` を送出してハンドラに委譲する方法も使えます。

障害ログは2種類に分かれます：
- **障害通知ログ** (FATAL/ERROR, ロガー名: `MONITOR`) → 監視専用ファイル
- **障害解析ログ** (FATAL/ERROR, ロガー名: クラス名) → アプリケーションログ

**注意点**:
- `HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージはリクエストスコープ（キー名デフォルト: `errors`）に設定されるのでViewで参照できます
- セキュリティ要件により個人情報・機密情報をログに出力できない場合は `FailureLogFormatter` をカスタマイズする必要があります
- `HttpErrorHandler` の `defaultPages` 機能を使う場合は `web.xml` にも `error-page` 設定が必要です

参照:
- `component/handlers/handlers-HttpErrorHandler.json#s4`
- `component/handlers/handlers-HttpErrorHandler.json#s6`
- `component/handlers/handlers-global-error-handler.json#s4`
- `component/libraries/libraries-failure-log.json#s1`
- `component/libraries/libraries-failure-log.json#s3`
- `processing-pattern/web-application/web-application-forward-error-page.json#s1`