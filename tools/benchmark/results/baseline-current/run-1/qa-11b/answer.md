**結論**: Nablarchでは、エラー発生時の画面表示とログ出力は複数のハンドラと障害ログユーティリティが連携して処理される。

## エラー処理の全体像

Nablarchのエラー処理は主に以下の3つの仕組みで構成される。

### 1. グローバルエラーハンドラ（バッチ・メッセージング共通）

`GlobalErrorHandler` がハンドラキューの上位に配置され、捕捉した例外・エラーに応じてログを出力する。

| 例外・エラー | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力後、結果として返却 |
| `Result.Error`（サブクラス含む） | FATAL レベルでログ出力後、返却 |
| `StackOverflowError` | FATAL レベルでログ出力後、`InternalError` に包んで返却 |
| `OutOfMemoryError` | 標準エラー出力に出力 → FATAL ログ出力後、`InternalError` で返却 |
| `ThreadDeath` | INFO レベルでログ出力後、リスロー |
| その他すべての例外 | FATAL レベルでログ出力後、`InternalError` に包んで返却 |

カスタマイズが必要な場合は、プロジェクト固有のエラー処理ハンドラを作成する。

### 2. HTTPエラーハンドラ（Webアプリ）

`HttpErrorHandler` が HTTP ステータスコードとログ出力を制御する。

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | 出力なし（業務エラーのため） | `getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| その他の例外・エラー | FATAL | 500 |

エラー画面のデフォルトページはステータスコードのパターンで設定できる：
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

### 3. アクション単位のエラー画面制御

個別のアクションメソッドに `@OnError` アノテーションで遷移先を指定できる：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

システム全体で共通のエラーページに遷移させる場合は、カスタムハンドラを作成する方法が推奨される。

### 4. 障害ログ（FailureLog）

障害ログには2種類ある：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL、ERROR | `MONITOR` |
| 障害解析ログ（アプリ全体ログ） | FATAL、ERROR | クラス名 |

アプリコードから障害ログを出力するには `FailureLogUtil` を使用する：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

**注意点**:
- `HttpErrorHandler` の `defaultPages` 機能を使う場合、`web.xml` の `error-page` 要素との重複設定が必要。未設定だとWebサーバのデフォルトエラーページが表示されるため、`web.xml` への設定を推奨。
- `GlobalErrorHandler` の動作はカスタマイズ不可。要件が合わない場合はプロジェクト独自のハンドラを作成する。
- セキュリティ要件で個人情報・機密情報をログ出力できない場合、`FailureLogFormatter` のプレースホルダ処理をカスタマイズする必要がある。
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置すること。

参照:
- `component/handlers/handlers-global-error-handler.json#s4`
- `component/handlers/handlers-HttpErrorHandler.json#s4`
- `component/handlers/handlers-HttpErrorHandler.json#s6`
- `component/libraries/libraries-failure-log.json#s1`
- `component/libraries/libraries-failure-log.json#s3`
- `component/libraries/libraries-failure-log.json#s4`
- `processing-pattern/web-application/web-application-forward-error-page.json#s1`
- `component/handlers/handlers-on-error.json#s3`