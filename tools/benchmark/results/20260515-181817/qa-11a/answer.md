**結論**: Nablarch 6 のエラー処理は、**ハンドラによる例外捕捉・ログ出力**と**エラー画面への遷移**の 2 つの仕組みで構成されている。処理方式（Web / バッチ）によって使用するハンドラが異なる。

**根拠**:

### 1. Web アプリケーションのエラー処理：HTTPエラー制御ハンドラ

`nablarch.fw.web.handler.HttpErrorHandler` が後続ハンドラの例外を捕捉し、ログ出力とエラーレスポンスへの変換を行う。

| 例外・エラー | ログ | レスポンス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse`（業務例外） | ログ出力なし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | 設定による（`writeFailureLogPattern` で制御） | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外 | FATAL | 500 |

`ApplicationException` を原因とする `HttpErrorResponse` の場合、エラーメッセージを `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に格納し、View 側で参照できるようにする。

**エラー画面の設定**は `defaultPages` プロパティで HTTP ステータスコードのパターンに対して遷移先 JSP を指定する：

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

なお、デフォルトのエラーページ設定は `web.xml` の `error-page` 要素で行うことが推奨されている。

### 2. バッチ・メッセージングのエラー処理：グローバルエラーハンドラ

`nablarch.fw.handler.GlobalErrorHandler` が未捕捉例外・エラーを捕捉してログ出力し、処理結果を返す。ハンドラキューの先頭に配置する。

| 例外・エラー | 処理内容 |
|---|---|
| `ServiceError` | `ServiceError#writeLog()` でログ出力（レベルは実装クラスに依存） |
| `Result.Error` | FATAL ログ出力後、`Result.Error` を返却 |
| `ThreadDeath` | INFO ログ出力後、リスロー |
| `StackOverflowError` / `OutOfMemoryError` | FATAL ログ出力後、`InternalError` を生成して返却 |
| 上記以外 | FATAL ログ出力後、`InternalError` を生成して返却 |

### 3. エラー画面遷移のカスタマイズ

システム全体で共通エラー画面に遷移させたい場合は、専用ハンドラを作成してハンドラキューに追加する：

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context) {
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    } catch (OptimisticLockException e) {
      throw new HttpErrorResponse(
          400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
    }
  }
}
```

### 4. 障害ログの出力方針

障害ログは 2 種類に分かれ、それぞれ別ファイルに出力される：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL、ERROR | `MONITOR` |
| 障害解析ログ | FATAL、ERROR | クラス名 |

アプリケーションから直接障害ログを出力する場合は `FailureLogUtil` を使用する：

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

バッチ処理で後続処理継続せずに終了する場合は `TransactionAbnormalEnd` / `ProcessAbnormalEnd` を送出し、グローバルエラーハンドラに出力を委ねる：

```java
throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
// または
throw new ProcessAbnormalEnd(100, e, "USER_NOT_FOUND");
```

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置する必要がある
- `GlobalErrorHandler` はハンドラキューの先頭に配置すること。手前で例外が発生した場合はアプリケーションサーバが処理する
- `GlobalErrorHandler` は設定で実装を切り替えられないため、ログレベルを細かく制御したい場合はプロジェクト固有のハンドラを作成する
- 障害解析ログに個人情報・機密情報を出力するセキュリティ制約がある場合は `FailureLogFormatter` をカスタマイズする

参照: `handlers-HttpErrorHandler.json#s4`, `handlers-HttpErrorHandler.json#s5`, `handlers-HttpErrorHandler.json#s6`, `handlers-global-error-handler.json#s4`, `web-application-forward-error-page.json#s1`, `libraries-failure-log.json#s1`, `libraries-failure-log.json#s3`, `libraries-failure-log.json#s4`