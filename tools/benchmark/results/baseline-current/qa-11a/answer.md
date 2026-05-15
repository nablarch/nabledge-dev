**結論**: ウェブアプリケーションのエラー処理は、主に **HttpErrorHandler**（エラーレスポンス → エラー画面への遷移 + ログ出力）と**障害ログライブラリ**（FATALレベルのログ出力）の組み合わせで実現されます。エラー画面への遷移先は、ハンドラまたはアクションの `@OnError` アノテーションで制御します。

**根拠**:

### 1. HttpErrorHandler — 例外の種類に応じたログ出力とレスポンス

`HttpErrorHandler` がハンドラキュー内の後続で発生した例外を捕捉し、例外の種類に応じてログレベル・ステータスコードを決定します。

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | 設定による（`writeFailureLogPattern` 正規表現マッチで FATAL） | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージをリクエストスコープ（デフォルトキー: `errors`）に設定してビューで参照できるようにします。

### 2. デフォルトエラーページの設定

`HttpErrorHandler` の `defaultPages` プロパティで、ステータスコードパターンに対応したデフォルトページを設定できます。

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

ただし、`defaultPages` を使う場合は `web.xml` の `error-page` 要素にも同様の設定が必要です。推奨はデフォルトエラーページを `web.xml` で設定することです。

### 3. エラー画面への遷移先の指定方法

**方法A: システム共通のエラーハンドラ（推奨）**

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

**方法B: アクションメソッドへの `@OnError` アノテーション**

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**方法C: アクション内の `try-catch`**

```java
try {
    service.save(entity);
} catch (ApplicationException e) {
    throw new HttpErrorResponse("forward://index", e);
}
```

### 4. 障害ログの出力方針

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール向け） | FATAL、ERROR | `MONITOR` |
| 障害解析ログ（詳細調査向け） | FATAL、ERROR | クラス名 |

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

**注意点**:

- `OnError` アノテーションに指定できる `type` 属性は `RuntimeException` およびそのサブクラスのみです
- システム全体で遷移先を統一する場合は、個別のアクションに `@OnError` を設定する方法だと漏れが発生しやすいため、共通エラーハンドラの実装が推奨されます
- `HttpErrorResponse` が発生した場合、`HttpErrorHandler` はログを出力しません（業務例外として正常なフローとみなされるため）
- 障害ログに出力されるメッセージはメッセージ管理から障害コードで取得します。メッセージが見つからない場合は WARN レベルで別途ログが出力されます

参照: component/handlers/handlers-HttpErrorHandler.json#s4, #s5, #s6 / component/libraries/libraries-failure-log.json#s1, #s3 / processing-pattern/web-application/web-application-forward-error-page.json#s1, #s2 / component/handlers/handlers-on-error.json#s3