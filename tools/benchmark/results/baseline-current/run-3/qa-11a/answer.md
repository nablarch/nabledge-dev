**結論**: Nablarch のエラー処理は「ハンドラによる例外捕捉」「ログ出力（障害ログ）」「エラーページ遷移」の3層で構成されています。処理方式（Web/バッチ等）に応じて使用するハンドラが異なります。

## 1. ハンドラによる例外捕捉とログ出力

### グローバルエラーハンドラ（`nablarch.fw.handler.GlobalErrorHandler`）

全処理方式共通のハンドラ。ハンドラキューの**先頭に配置**し、後続ハンドラで発生した未捕捉例外を捕捉します。

| 例外/エラー | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | 実装クラス依存 | `ServiceError#writeLog` を呼び出してログ出力し、結果として返却 |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後、`Result.Error` を返却 |
| 上記以外の例外 | FATAL | ログ出力後、`InternalError` を生成して返却 |
| `ThreadDeath` | INFO | ログ出力後、リスロー |
| `StackOverflowError` | FATAL | ログ出力後、`InternalError` を生成して返却 |
| `OutOfMemoryError` | FATAL | 標準エラー出力にも出力後、`InternalError` を生成して返却 |
| その他 `VirtualMachineError` | FATAL | ログ出力後、リスロー |

カスタマイズが必要な場合（ログレベルを細かく変えたいなど）は、プロジェクト固有のエラー処理ハンドラを新規作成します。

### HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

Webアプリケーション専用。後続ハンドラで発生した例外に対してログ出力とHTTPレスポンスへの変換を行います。

| 例外 | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `getResponse()` の値 |
| `Result.Error` | FATAL（条件付き） | `getStatusCode()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外 | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、メッセージ情報を `ErrorMessages` に変換してリクエストスコープに設定（デフォルトキー: `errors`）することで、View でエラーメッセージを表示できます。

## 2. エラーページの設定

`HttpErrorHandler` の `defaultPages` プロパティで設定します。

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="404" value="/NOT_FOUND.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
      <entry key="503" value="/NOT_IN_SERVICE.jsp" />
    </map>
  </property>
</component>
```

推奨: この機能よりも `web.xml` の `error-page` 要素でデフォルトエラーページを設定することが推奨されています。

## 3. 障害ログの出力

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL / ERROR | MONITOR |
| 障害解析ログ | FATAL / ERROR | クラス名 |

アプリケーションで障害ログを出力する場合は `FailureLogUtil` を使用します。

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

バッチ処理では `TransactionAbnormalEnd` または `ProcessAbnormalEnd` をスローして例外ハンドラに委譲します。

## 4. 一般ログの出力

```java
private static final Logger LOGGER = LoggerManager.get(UserManager.class);
LOGGER.logDebug("message");
```

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler` より後ろ、かつ `HttpAccessLogHandler` より後ろに配置する必要があります
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置してください
- 障害通知ログのロガー名は `MONITOR` とし、専用ファイルへ出力することで監視ツールとの連携が容易になります

参照: `handlers-HttpErrorHandler.json#s4`, `handlers-HttpErrorHandler.json#s6`, `handlers-global-error-handler.json#s4`, `libraries-failure-log.json#s1`, `libraries-failure-log.json#s3`, `libraries-log.json#s6`