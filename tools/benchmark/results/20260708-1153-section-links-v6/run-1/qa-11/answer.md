**結論**: ウェブアプリケーションのエラー処理は「HTTPエラー制御ハンドラ（HttpErrorHandler）」が中心となり、例外の種類に応じてログ出力とHTTPレスポンス（エラー画面）を生成する。エラー画面への遷移先はハンドラまたはアクションの `@OnError` アノテーションで設定する。

**根拠**:

**1. HTTPエラー制御ハンドラによるログ出力とレスポンス生成**

後続ハンドラで発生した例外を捕捉し、以下のように処理する：

| 例外の種類 | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException`（アクションなし） | INFO | 404 |
| `HttpErrorResponse`（業務エラー） | ログなし | `HttpErrorResponse#getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException`（バリデーションエラーなど）の場合は、メッセージ情報を `ErrorMessages` に変換してリクエストスコープ（キー名: `errors`）に設定するため、JSPでエラーメッセージを表示できる。

**2. デフォルトエラーページの設定**

`defaultPages` でHTTPステータスコードに対応するページを設定できる：

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

**3. エラー画面への遷移先指定方法**

機能詳細（エラー時の画面遷移とステータスコード）では以下の方法が提供されている：

- **ステータスコード対応のデフォルトページ**: `HttpErrorHandler` の `defaultPages` で設定
- **ハンドラで共通制御**: 例外種別を捕捉するカスタムハンドラを作成

  ```java
  public class ExampleErrorForwardHandler implements Handler<Object, Object> {
    public Object handle(Object data, ExecutionContext context) {
      try {
        return context.handleNext(data);
      } catch (NoDataException e) {
        throw new HttpErrorResponse(404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
      }
    }
  }
  ```

- **アクション単位で指定**: `@OnError` アノテーション

  ```java
  @OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
  public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
  ```

**4. 障害ログの出力方針**

障害ログは2種類に分かれており、ロガー名で出力先を分離する：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール用） | FATAL、ERROR | `MONITOR` |
| 障害解析ログ（アプリケーションログ） | FATAL、ERROR | クラス名 |

参照:
- HTTPエラー制御ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md
  例外の種類に応じた処理とレスポンスの生成
  nablarch.fw.Result.Errorのログ出力について
  デフォルトページの設定
- グローバルエラーハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md
  例外及びエラーに応じた処理内容
- OnErrorインターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md
  OnErrorを使用する
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
  エラー時の画面遷移とステータスコード
- エラー時の遷移先の指定方法
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md
  ハンドラで共通の振る舞いを定義する
- 障害ログの出力
  .claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md
  障害ログの出力方針