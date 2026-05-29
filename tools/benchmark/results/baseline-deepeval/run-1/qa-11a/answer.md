十分な情報が集まりました。回答を生成します。

---

**結論**: ウェブアプリケーションのエラー処理は、主に**HTTPエラー制御ハンドラ**（`HttpErrorHandler`）と**グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担い、例外の種類に応じてログ出力とエラー画面への遷移を自動的に行う。

---

**根拠**:

## エラー処理の全体像

エラー処理はハンドラキューにより階層的に処理される。

```
グローバルエラーハンドラ  ← ハンドラキューの先頭（最後の砦）
  HTTPレスポンスハンドラ
    HTTPアクセスログハンドラ
      HTTPエラー制御ハンドラ  ← エラー画面へのレスポンス変換
        業務処理ハンドラ群...
```

---

## 1. HTTPエラー制御ハンドラ（`HttpErrorHandler`）の動作

後続ハンドラで発生した例外をキャッチし、**ログ出力**と**エラー用HttpResponseの生成**を行う。

| 例外クラス | ログ出力 | レスポンス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` の値 |
| `Result.Error` | `writeFailureLogPattern`設定に従う | `Error#getStatusCode()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException`（業務例外）の場合は、エラーメッセージをリクエストスコープの `errors` キーに格納し、View側で参照できるようにする。

### デフォルトエラーページの設定

ステータスコードに対応したデフォルトページを設定できる（推奨は`web.xml`で設定）。

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

---

## 2. エラー時の画面遷移を指定する方法

### アクションメソッドごとに指定（`@OnError`）

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

### システム全体で共通のエラーページへ遷移（カスタムハンドラ）

個別アクションに指定すると漏れが生じるため、共通ハンドラを追加する方法が推奨される。

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

---

## 3. 障害ログの出力

障害ログは**障害通知ログ**と**障害解析ログ**の2種類で管理される。

| 種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | 監視専用ファイル（監視ツールで検知） |
| 障害解析ログ | FATAL/ERROR | クラス名 | アプリケーションログ（スタックトレース付き） |

```properties
# log.properties（設定例）
writer.monitorLog.filePath=/var/log/app/monitor.log   # 監視ログ
writer.appLog.filePath=/var/log/app/app.log           # 解析ログ

loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorLog
```

アプリケーションコードから障害ログを出力する場合は `FailureLogUtil` を使用する。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` と `HTTPアクセスログハンドラ` より後ろに配置する必要がある
- `GlobalErrorHandler` は `HttpErrorHandler` を超えてきた未捕捉の例外を処理するため、できるだけハンドラキューの先頭に配置する
- デフォルトエラーページは `defaultPages` プロパティよりも `web.xml` の `error-page` 要素で設定することを推奨（発生場所によってはウェブサーバのデフォルトページが表示されるため）

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-on-error.json:s3, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1, libraries-failure-log.json:s3

---