**結論**: Nablarch のエラー処理は、**グローバルエラーハンドラ**（例外の捕捉とログ出力）、**HTTPエラーハンドラ**（エラー画面へのルーティング）、**障害ログ機能**（通知ログと解析ログの二段階出力）の3層で構成されています。

**根拠**:

### 1. グローバルエラーハンドラ（例外の捕捉とログ出力）

`GlobalErrorHandler` がハンドラキューの先頭に配置され、未捕捉の例外・エラーをすべて捕捉します。例外の種別に応じてログレベルが変わります。

| 例外/エラー | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` による（実装クラスに依存） | `ServiceError` を結果として返却 |
| `Result.Error`（サブクラス含む） | FATAL | `Result.Error` を結果として返却 |
| 上記以外の例外 | FATAL | `InternalError` に変換して返却 |
| `ThreadDeath` | INFO | 再スロー |
| `StackOverflowError` | FATAL | `InternalError` に変換して返却 |
| `OutOfMemoryError` | FATAL（標準エラー出力にも出力） | `InternalError` に変換して返却 |

> **注意**: このハンドラはできるだけハンドラキューの先頭に配置すること。先頭より手前のハンドラで例外が発生した場合は、アプリケーションサーバやJVMによる処理になります。

### 2. HTTPエラーハンドラ（エラー画面へのルーティング）

`HttpErrorHandler` はWebアプリケーション用のエラー処理を担い、例外種別とHTTPステータスコードを対応付けます。

| 例外/エラー | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし（業務エラーのため） | `getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外 | FATAL | 500 |

エラー画面のデフォルトページはコンポーネント設定で指定します。

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

> **推奨**: デフォルトのエラーページ設定は `web.xml` の `error-page` 要素で行うことが推奨されています。`defaultPages` 機能を使うと `web.xml` 側にも同様の設定が必要になります。

### 3. アクション個別のエラー遷移（OnErrorアノテーション）

業務アクションのメソッドに `@OnError` を設定することで、特定の例外が発生した場合の遷移先を指定できます。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

システム全体で共通エラーページに遷移させたい場合は、個別アノテーションではなくエラー遷移専用のハンドラを追加する方式が推奨されています（アノテーション漏れや指定ミスのリスク低減のため）。

### 4. 障害ログの出力（二段階ログ設計）

障害ログは「障害通知ログ」と「障害解析ログ」の2種類があります。

| ログの種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL、ERROR | `MONITOR` | ログ監視ツールによる障害検知 |
| 障害解析ログ | FATAL、ERROR | クラス名 | アプリケーションログでの詳細解析 |

アプリケーションコードから障害ログを出力するには `FailureLogUtil` を使用します。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

バッチ・メッセージングの場合は `TransactionAbnormalEnd` や `ProcessAbnormalEnd` をスローして例外ハンドラに障害ログ出力を委譲します。

```java
throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
```

**注意点**:
- `GlobalErrorHandler` はハンドラキューの**先頭**に置くこと。先頭より前のハンドラで発生した例外は捕捉できません。
- スレッドコンテキスト情報をログに含めたい場合は、`ThreadContextClearHandler`（スレッドコンテキスト変数削除ハンドラ）より**後ろ**に配置すること。
- `Result.Error` のログ出力は `writeFailureLogPattern` プロパティの正規表現設定によって制御されます（`getStatusCode()` とのマッチで判定）。
- 障害ログにはデフォルト障害コード（`failureLogFormatter.defaultFailureCode`）の設定が**必須**です。
- セキュリティ要件により個人情報・機密情報のログ出力が禁止される場合は、`FailureLogFormatter` のプレースホルダ出力処理をカスタマイズすること。

参照:
- component/handlers/handlers-global-error-handler.json#s4
- component/handlers/handlers-HttpErrorHandler.json#s4
- component/handlers/handlers-HttpErrorHandler.json#s5
- component/handlers/handlers-HttpErrorHandler.json#s6
- component/handlers/handlers-on-error.json#s3
- component/libraries/libraries-failure-log.json#s1
- component/libraries/libraries-failure-log.json#s3
- component/libraries/libraries-failure-log.json#s4
- processing-pattern/web-application/web-application-forward-error-page.json#s1