**結論**: ウェブアプリケーションのエラーハンドリングは、主に「HTTPエラー制御ハンドラ (`HttpErrorHandler`)」と「グローバルエラーハンドラ (`GlobalErrorHandler`)」の2層で構成され、ログ出力は例外の種類に応じてFATAL/INFOレベルで自動的に行われる。エラー画面への遷移先は `@OnError` インターセプタやハンドラで制御する。

---

**根拠**:

#### 1. HTTPエラー制御ハンドラ（ウェブアプリケーションの中心的なエラー処理）

`nablarch.fw.web.handler.HttpErrorHandler` がハンドラキューに配置され、後続ハンドラで発生した例外に対してログ出力とHTTPレスポンスへの変換を行う。

| 例外の種類 | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException`（ハンドラ未存在）| INFO | 404 |
| `HttpErrorResponse`（業務例外によるエラーレスポンス）| ログなし | `HttpErrorResponse#getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合、`ErrorMessages` に変換してリクエストスコープのキー名 `errors`（変更可）にセットするため、JSPで `${errors}` としてエラーメッセージを表示できる。

`Result.Error` に対するログ出力は `writeFailureLogPattern` プロパティで制御する（正規表現でステータスコードとマッチした場合にFATALログ出力）。

デフォルトのエラーページはコンポーネント設定で指定できるが、`web.xml` の `error-page` 要素での設定が推奨される：

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

#### 2. グローバルエラーハンドラ（バッチ等の共通エラー処理）

`nablarch.fw.handler.GlobalErrorHandler` はハンドラキューの先頭に配置し、未捕捉例外・エラーを捕捉してログ出力する。ウェブアプリケーションでも使用される。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog()` を呼び出し（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力 |
| 上記以外の例外 | FATALレベルのログ出力 → `InternalError` を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルのログ出力 → `InternalError` を返却 |
| `ThreadDeath` / `VirtualMachineError`（StackOverflow/OOM以外） | ログ出力後にリスロー |

このハンドラは設定では実装を切り替えられないため、ログレベルを細かく制御したい場合はプロジェクト固有のエラー処理ハンドラを作成する。

#### 3. エラー画面への遷移先の制御

**アクションレベルで個別指定（`@OnError` / `@OnErrors`）**:

```java
// 単一例外に対して遷移先を指定
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }

// 複数例外に対して遷移先を指定（サブクラスから先に定義すること）
@OnErrors({
    @OnError(type = UserLockedException.class, path = "/WEB-INF/view/login/locked.jsp"),
    @OnError(type = ApplicationException.class, path = "/WEB-INF/view/login/index.jsp")
})
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

**ハンドラレベルで共通化（推奨）**:

システム全体で共通のエラーページに遷移させる場合は、個別アクションへのアノテーション指定では漏れが発生しやすいため、ハンドラを追加して対応する：

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

#### 4. 障害ログの出力方針

障害ログは2種類に分けて出力する：

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL、ERROR | `MONITOR` | 障害通知専用ファイル（ログ監視ツールで監視） |
| 障害解析ログ | FATAL、ERROR | クラス名 | アプリケーションログ |

設定は `log.properties` と `app-log.properties` に記述する：

```properties
# app-log.properties
failureLogFormatter.defaultFailureCode=UNEXPECTED_ERROR
failureLogFormatter.defaultMessage=an unexpected exception occurred.
failureLogFormatter.notificationFormat=fail_code = [$failureCode$] $message$
failureLogFormatter.analysisFormat=fail_code = [$failureCode$] $message$\nInput Data :\n$data$
```

アプリケーションコードから `FailureLogUtil` で明示的に障害ログを出力することもできる：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

**注意点**: 
- `@OnError` では単一の例外クラスに対して1つの遷移先しか指定できない。同じ例外クラスで複数の遷移先が必要な場合は、アクションメソッド内で `try-catch` を使って `HttpErrorResponse` を生成する。
- `GlobalErrorHandler` はハンドラキューのできるだけ先頭に配置すること。このハンドラより手前で例外が発生した場合は、アプリケーションサーバやJVMによって例外処理が行われる。
- デフォルトのエラーページ設定は、`HttpErrorHandler` の `defaultPages` よりも `web.xml` の `error-page` 要素への設定が推奨される。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, handlers-global-error-handler.json:s5, handlers-on-error.json:s3, handlers-on-errors.json:s3, libraries-failure-log.json:s1, web-application-forward-error-page.json:s1