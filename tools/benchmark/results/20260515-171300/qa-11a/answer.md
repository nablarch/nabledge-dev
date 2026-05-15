**結論**: Nablarch 6 では、エラー発生時の**エラー画面表示**と**ログ出力**は主に以下の3層で処理される。①ハンドラ（HttpErrorHandler / GlobalErrorHandler）による自動ログ出力、②障害ログライブラリ（FailureLogUtil）による明示的なログ出力、③OnErrorアノテーションやカスタムハンドラによるエラー画面遷移の制御。

**根拠**:

### 1. ログ出力の仕組み

#### HttpErrorHandler（Webアプリ）
後続ハンドラで発生した例外の種類に応じて自動的にログ出力とHTTPレスポンスを生成する：

| 例外 | ログレベル | ステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし（業務例外のため） | 任意 |
| `Result.Error` | 設定による（`writeFailureLogPattern`） | 任意 |
| `StackOverflowError` | FATAL | 500 |
| その他例外 | FATAL | 500 |

#### GlobalErrorHandler（バッチ・汎用）
例外の種類に応じてログを出力する：

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError` | `writeLog()`を呼び出しログ出力、実装クラスによりレベル異なる |
| `Result.Error` | FATALレベルでログ出力 |
| その他例外 | FATALレベルでログ出力し `InternalError` に変換 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルでログ出力（OOMは標準エラーにも出力） |

> **配置の注意**: GlobalErrorHandlerはハンドラキューの先頭付近に配置すること。

#### 障害ログの出力方針
障害ログは2種類に分けて出力される：

| ログ種類 | レベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL / ERROR | `MONITOR` |
| 障害解析ログ（アプリログ） | FATAL / ERROR | クラス名 |

#### 明示的な障害ログ出力（FailureLogUtil）
業務コードから障害ログを出力する場合は `FailureLogUtil` を使用する：

```java
// Webアプリ等で直接出力する場合
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");

// バッチ・メッセージングでは例外送出でハンドラに委譲
throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
throw new ProcessAbnormalEnd(100, e, "USER_NOT_FOUND");
```

### 2. エラー画面表示の仕組み

#### HttpErrorHandler — デフォルトエラーページの設定
HTTPステータスコードパターンでJSPを対応付ける：

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

#### OnErrorアノテーション — アクションごとの遷移先指定
業務アクションのメソッドに `@OnError` を付与して例外発生時の遷移先を指定する：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

エラー画面にDB取得データを渡す場合は内部フォワードを使用する：

```java
@OnError(type = ApplicationException.class, path = "forward://initializeRegisterPage")
public HttpResponse confirmForRegister(...) { ... }
```

#### カスタムハンドラ — システム共通のエラー画面
`@OnError` を全アクションに付与する代わりに、共通ハンドラで一括制御できる：

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

**注意点**:
- `HttpErrorResponse`（業務例外）はログ出力されない。バリデーションエラー等の業務上の想定エラーは意図的にログ非出力となっている。
- `defaultPages` を使用する場合、`web.xml` の `<error-page>` 設定と重複するため、Nablarch公式はデフォルトエラーページを `web.xml` 側で設定することを推奨している。
- GlobalErrorHandlerはハンドラキューの先頭に配置しないと、その手前で発生した例外は処理されない。

参照: `component/handlers/handlers-HttpErrorHandler.json#s4`, `component/handlers/handlers-HttpErrorHandler.json#s5`, `component/handlers/handlers-HttpErrorHandler.json#s6`, `component/handlers/handlers-global-error-handler.json#s4`, `component/libraries/libraries-failure-log.json#s1`, `component/libraries/libraries-failure-log.json#s3`, `component/handlers/handlers-on-error.json#s3`, `processing-pattern/web-application/web-application-forward-error-page.json#s1`