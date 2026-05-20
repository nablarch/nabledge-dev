**結論**: ウェブアプリケーションのエラー処理は、`HttpErrorHandler`（HTTPエラー制御ハンドラ）がハンドラキュー内で例外を捕捉してログ出力・エラーレスポンス生成を担い、エラー画面への遷移は `@OnError` インターセプタまたはカスタムハンドラで制御する。

**根拠**:

**① HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）**

後続ハンドラで発生した例外に対し、例外の種類に応じてログレベルとHTTPステータスコードが決まる：

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | 設定による（`writeFailureLogPattern` の正規表現マッチで FATAL） | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合、フレームワークが保持するメッセージ情報を `ErrorMessages` に変換してリクエストスコープ（デフォルトキー名: `errors`）に設定し、Viewでエラーメッセージを扱えるようにする。

**② エラー画面（デフォルトページ）の設定**

ステータスコードに対応したデフォルトエラーページは `HttpErrorHandler` の `defaultPages` で設定する：

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

ただし、デフォルトエラーページの設定は `web.xml` の `error-page` 要素で行うことを推奨する。

**③ アクション個別のエラー遷移先指定（`@OnError` インターセプタ）**

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

`type` 属性には `RuntimeException` およびそのサブクラスを指定できる。バリデーションエラーの遷移先指定にも利用できる。

**④ システム共通のエラーページへの遷移（カスタムハンドラ）**

全アクションに統一的なエラーハンドリングを適用したい場合は、カスタムハンドラをハンドラキューに追加する：

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

**⑤ 障害ログ（`FailureLogUtil`）**

障害ログには「障害通知ログ」と「障害解析ログ」の2種類がある：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL、ERROR | MONITOR |
| 障害解析ログ | FATAL、ERROR | クラス名 |

アプリケーションから障害ログを出力する場合：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置すること
- `GlobalErrorHandler`（`nablarch.fw.handler.GlobalErrorHandler`）は未捕捉の例外・エラーを捕捉するためできるだけハンドラキューの先頭に配置すること
- `@OnError` では単一の例外に対して複数の遷移先は指定できないため、複数遷移先が必要な場合はアクションメソッド内で `try-catch` を使う

参照: component/handlers/handlers-HttpErrorHandler.json:s4, component/handlers/handlers-HttpErrorHandler.json:s5, component/handlers/handlers-HttpErrorHandler.json:s6, component/handlers/handlers-global-error-handler.json:s4, processing-pattern/web-application/web-application-feature-details.json:s16, processing-pattern/web-application/web-application-forward-error-page.json:s1, component/handlers/handlers-on-error.json:s3, component/libraries/libraries-failure-log.json:s1, component/libraries/libraries-failure-log.json:s3