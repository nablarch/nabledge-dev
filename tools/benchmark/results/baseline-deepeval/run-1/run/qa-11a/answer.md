**結論**: ウェブアプリケーションのエラー画面表示とログ出力は、主に **HTTPエラー制御ハンドラ（`HttpErrorHandler`）** が担当し、例外の種類に応じてログレベルとレスポンスを決定する。さらに上位の **グローバルエラーハンドラ（`GlobalErrorHandler`）** が未捕捉例外の最終受け口となる。

---

**根拠**

**1. HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）**

後続ハンドラで発生した例外を捕捉し、ログ出力とエラー用 `HttpResponse` の生成を行う。例外の種類に応じた処理は以下の通り。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しない |
| `HttpErrorResponse` | なし | `HttpErrorResponse#getResponse()` | 業務例外（バリデーション等）はログ不要 |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern` で制御 |
| `StackOverflowError` | FATAL | 500 | 実装バグ等の障害 |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外はすべて障害扱い |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージを JSP 側で扱えるよう `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に設定する。

```xml
<!-- キー名を変更したい場合 -->
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

エラー画面のデフォルトページはハンドラの `defaultPages` プロパティで設定できる。

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

**2. グローバルエラーハンドラ（`nablarch.fw.handler.GlobalErrorHandler`）**

ハンドラキュー先頭に配置し、未捕捉の例外・エラーを最終的に受け取る。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError` | `ServiceError#writeLog` を呼び出しログ出力 |
| `Result.Error` | FATAL レベルログを出力 |
| 上記以外の例外 | FATAL レベルログを出力し `InternalError` を生成して返却 |

**3. エラー画面への遷移指定方法（3つのアプローチ）**

**①アクションメソッドに `@OnError` アノテーションを付与する**（アクション個別に指定）
```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**②カスタムエラーハンドラをハンドラキューに追加する**（システム共通のエラーページへ誘導したい場合に推奨）
```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
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

**4. 障害ログの出力方針**

障害ログは2種類のログを別ファイルに出力する。

| 種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | ログ監視ツールで障害を検知 |
| 障害解析ログ | FATAL/ERROR | クラス名 | アプリケーション全体ログへ出力 |

---

**注意点**

- `HttpErrorHandler` の `defaultPages` と `web.xml` の `error-page` 要素が重複すると JSP 設定が二重になる。デフォルトエラーページは **`web.xml` への設定を推奨**する。
- システム全体で共通のエラーページに遷移させたい場合、個別アクションへの `@OnError` 指定ではなくカスタムハンドラで対応することで、設定漏れ・指定ミスを防ぎやすい。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-on-error.json:s3, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1

---