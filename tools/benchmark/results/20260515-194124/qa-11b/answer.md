**結論**: Nablarch 6 でエラー発生時にエラー画面を表示したり、ログを出力する仕組みは、主に **HTTPエラー制御ハンドラ**（Webアプリ用）と **グローバルエラーハンドラ**（全処理方式共通）の2つのハンドラが担っている。障害ログの出力には専用の **障害ログ機能**（`FailureLogUtil`）が提供されている。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（Webアプリ専用）

クラス名: `nablarch.fw.web.handler.HttpErrorHandler`

後続ハンドラで発生した例外を捕捉し、**例外の種類に応じてログ出力レベルとHTTPレスポンスを決定**する。

| 例外の種類 | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし（業務エラーのため） | `getResponse()` の値 |
| `Result.Error` | 設定による（`writeFailureLogPattern`）| `getStatusCode()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外/エラー | FATAL | 500 |

`HttpErrorResponse` の原因が `ApplicationException` の場合、エラーメッセージ情報を `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に設定し、View 側で参照できるようにする。

**エラー画面の設定例**（`defaultPages`）:
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

> **注意**: `defaultPages` よりも `web.xml` の `<error-page>` 要素でのデフォルトエラーページ設定が推奨される。

**配置上の制約**:
- HTTPレスポンスハンドラより**後ろ**に配置すること
- HTTPアクセスログハンドラより**後ろ**に配置すること

### 2. グローバルエラーハンドラ（全処理方式共通）

クラス名: `nablarch.fw.handler.GlobalErrorHandler`

ハンドラキューの**できるだけ先頭**に配置し、未捕捉の例外・エラーを捕捉してログ出力と結果返却を行う。

| 例外/エラー | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | ServiceError 実装クラスによる | `writeLog()` 呼び出し後、`ServiceError` を返却 |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後、`Result.Error` を返却 |
| 上記以外の例外 | FATAL | ログ出力後、`InternalError` を生成して返却 |
| `ThreadDeath` | INFO | リスロー |
| `StackOverflowError` | FATAL | `InternalError` を生成して返却 |
| `OutOfMemoryError` | FATAL | 標準エラー出力への出力後にログ出力、`InternalError` を生成して返却 |
| `VirtualMachineError`（StackOverflow/OOM以外） | FATAL | リスロー |

### 3. エラー時の遷移先（Webアプリ）

アクションメソッドに `@OnError` アノテーションを付けて例外ごとに遷移先を指定する:

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

システム全体で共通エラーページに遷移させる場合は、カスタムハンドラを追加する方式が推奨される:

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

### 4. 障害ログの出力

`FailureLogUtil` を使って障害ログを出力する。障害ログは **障害通知ログ**（MONITOR ロガー）と **障害解析ログ**（クラス名ロガー）の2種類に分かれる:

```java
// アプリケーションで明示的に出力する場合
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

設定（`app-log.properties`）:
```properties
failureLogFormatter.defaultFailureCode=MSG99999
failureLogFormatter.defaultMessage=an unexpected exception occurred.
failureLogFormatter.notificationFormat=fail_code = [$failureCode$] $message$
failureLogFormatter.analysisFormat=fail_code = [$failureCode$] $message$\nInput Data :\n$data$
```

---

**注意点**:

- `HttpErrorHandler` は**Webアプリ専用**。バッチやメッセージングでは `GlobalErrorHandler` が主なエラー処理担当となる。
- `GlobalErrorHandler` の動作はコンポーネント設定で変更不可。ログレベルを細かく制御したい場合はプロジェクト独自のハンドラを作成する必要がある。
- `HttpErrorHandler` の `defaultPages` でエラーページを設定した場合、`web.xml` の `<error-page>` 設定も合わせて必要（片方だけだとウェブサーバのデフォルトエラーページが表示される場合がある）。
- 障害ログに個人情報・機密情報の出力が許可されない場合は、`FailureLogFormatter` を継承してカスタマイズが必要。

参照: `component/handlers/handlers-HttpErrorHandler.json#s4`, `component/handlers/handlers-HttpErrorHandler.json#s6`, `component/handlers/handlers-global-error-handler.json#s4`, `component/handlers/handlers-on-error.json#s3`, `processing-pattern/web-application/web-application-forward-error-page.json#s1`, `component/libraries/libraries-failure-log.json#s1`, `component/libraries/libraries-failure-log.json#s3`