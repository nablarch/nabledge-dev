**結論**: ウェブアプリケーションのエラー処理は、**HTTPエラー制御ハンドラ**が例外の種類に応じてログ出力とHTTPレスポンスを制御し、エラー画面への遷移はアクションの`@OnError`アノテーションまたは共通ハンドラで設定する。

---

**根拠**:

### 1. HTTPエラー制御ハンドラによるログ出力とレスポンス

例外の種類に応じて以下の処理が行われる。

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | 設定による (`writeFailureLogPattern`) | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| その他の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージをリクエストスコープ（デフォルトキー: `errors`）に設定してViewで利用できるようにする。

`Result.Error` のログ出力は `writeFailureLogPattern` に正規表現を設定し、`Error#getStatusCode()` がマッチした場合にFATALレベルのログを出力する。

### 2. エラー画面の遷移設定

**方法1: デフォルトエラーページの設定（ハンドラ設定）**

ステータスコードに対応したデフォルトの遷移先ページをコンポーネント設定ファイルで指定できる。

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

> この機能を使用するのではなく、デフォルトのエラーページの設定は `web.xml` へ行うことを推奨する。

**方法2: 共通エラーハンドラの実装（システム全体統一）**

特定の例外に対してシステム全体で共通のエラーページに遷移させる場合は、カスタムハンドラを追加する。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context){
    try{
      return context.handleNext(data);
    } catch (NoDataException e){
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    } catch (OptimisticLockException e){
      throw new HttpErrorResponse(
          400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
    }
  }
}
```

**方法3: `@OnError` / `@OnErrors` アノテーション（アクション単位）**

```java
// 単一例外の場合
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }

// 複数例外の場合（サブクラスを先に定義すること）
@OnErrors({
    @OnError(type = UserLockedException.class, path = "/WEB-INF/view/login/locked.jsp"),
    @OnError(type = AuthenticationException.class, path = "/WEB-INF/view/login/index.jsp"),
    @OnError(type = ApplicationException.class, path = "/WEB-INF/view/login/index.jsp")
})
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

### 3. 障害ログの出力

障害ログは2種類に分かれる。

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL、ERROR | MONITOR |
| 障害解析ログ | FATAL、ERROR | クラス名 |

アプリケーションから明示的に障害ログを出力する場合は `FailureLogUtil` を使用する。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `@OnErrors` で継承関係にある例外を定義する場合は、必ずサブクラスの例外を先に定義すること。
- HTTPエラー制御ハンドラの `defaultPages` と `web.xml` のエラーページ設定が重複する場合、Servlet API側にも設定が必要。未設定の場合はウェブサーバのデフォルトページが表示される。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, web-application-forward-error-page.json:s1, handlers-on-error.json:s3, handlers-on-errors.json:s3, libraries-failure-log.json:s1, libraries-failure-log.json:s3