**結論**: Nablarchのエラー処理は、「ハンドラによるログ出力」と「インターセプタ/ハンドラによるエラー画面遷移」の2層構造になっている。

## エラーログの出力

### グローバルエラーハンドラ（`GlobalErrorHandler`）
ハンドラキューの**先頭**に配置し、未捕捉の例外・エラーを全て補足してFATALログを出力する。

| 例外/エラー | ログレベル |
|---|---|
| `ServiceError` | ServiceError実装クラスによる |
| `Result.Error` | FATAL |
| その他の例外 | FATAL |
| `ThreadDeath` | INFO（その後リスロー） |
| `StackOverflowError` | FATAL |
| `OutOfMemoryError` | FATAL（+ 標準エラー出力にも出力） |

クラス名: nablarch.fw.handler.GlobalErrorHandler

### HTTPエラー制御ハンドラ（`HttpErrorHandler`）
Webアプリケーション向け。例外の種類に応じてログ出力とHTTPレスポンスを生成する。

| 例外 | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | レスポンス依存 |
| `StackOverflowError` | FATAL | 500 |
| その他 | FATAL | 500 |

### 障害ログ（`FailureLogUtil`）
アプリケーションコードから明示的に障害ログを出力する場合は `FailureLogUtil` を使用する。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

障害ログは2種類に分けて出力する:
- **障害通知ログ**: ロガー名 `MONITOR` でFATAL/ERRORレベル → 監視ツール向けファイルに出力
- **障害解析ログ**: クラス名のロガーでFATAL/ERRORレベル → アプリケーションログに出力

## エラー画面の表示

### アクション単位の設定：`@OnError` / `@OnErrors`
アクションメソッドにアノテーションを付けて例外ごとの遷移先を指定する。

```java
@OnErrors({
    @OnError(type = UserLockedException.class, path = "/WEB-INF/view/login/locked.jsp"),
    @OnError(type = ApplicationException.class, path = "/WEB-INF/view/login/index.jsp")
})
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

### システム全体の共通エラーページ：カスタムハンドラ
個別アクションへのアノテーション設定を避け、ハンドラで一元管理する方法。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
    @Override
    public Object handle(Object data, ExecutionContext context) {
        try {
            return context.handleNext(data);
        } catch (NoDataException e) {
            throw new HttpErrorResponse(404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
        }
    }
}
```

### HTTPステータスコード別デフォルトページ：`HttpErrorHandler`の`defaultPages`設定

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
    </map>
  </property>
</component>
```

**注意点**:
- `GlobalErrorHandler` はハンドラキューの先頭に配置すること
- `HttpErrorHandler` は `HttpResponseHandler` より後ろに配置すること
- `@OnErrors` で継承関係のある例外を定義する場合はサブクラスを先に定義すること
- `defaultPages` よりも `web.xml` の `error-page` 要素で設定する方が推奨

参照: component/handlers/handlers-global-error-handler.json, component/handlers/handlers-HttpErrorHandler.json, component/handlers/handlers-on-error.json, component/handlers/handlers-on-errors.json, processing-pattern/web-application/web-application-forward-error-page.json, component/libraries/libraries-failure-log.json