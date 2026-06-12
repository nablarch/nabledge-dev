**結論**: Nablarch 6では、エラー処理は主に「ハンドラ」と「ログ出力ライブラリ」の2層で実現します。HTTPエラー制御ハンドラ（`HttpErrorHandler`）がエラー画面への遷移を担い、グローバルエラーハンドラ（`GlobalErrorHandler`）が未捕捉例外のログ出力を担います。

**根拠**:

### 1. エラー画面の表示 — `HttpErrorHandler`

`nablarch.fw.web.handler.HttpErrorHandler` が後続ハンドラで発生した例外を捕捉し、HTTPレスポンスに変換します。

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし（業務例外のため） | レスポンス内容による |
| `Result.Error` | 設定による（FATAL可） | `getStatusCode()`の値 |
| `StackOverflowError` | FATAL | 500 |
| それ以外の例外 | FATAL | 500 |

デフォルトエラーページの設定例：
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
推奨: デフォルトエラーページは`web.xml`の`error-page`要素で設定すること。

### 2. バリデーションエラーメッセージの画面表示

`HttpErrorResponse`の原因例外が`ApplicationException`の場合、`HttpErrorHandler`がリクエストスコープに`ErrorMessages`を格納します。Thymeleafではこれを参照して表示できます：

```html
<span th:if="${errors.hasError('form.userName')}"
      th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

### 3. アクション個別のエラー遷移 — `@OnError` / `@OnErrors`

特定のアクションメソッドで例外が発生したときの遷移先は`@OnError`で指定できます：
```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) { ... }
```

複数例外を扱う場合は`@OnErrors`を使用します。

### 4. システム全体の共通エラー遷移 — カスタムハンドラ

個別アクションへの指定漏れを防ぐには、独自ハンドラをハンドラキューに追加します：
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

### 5. ログ出力 — `GlobalErrorHandler` と 障害ログ

`nablarch.fw.handler.GlobalErrorHandler`はハンドラキューの先頭に配置し、未捕捉例外を捕捉してFATALログを出力します。

障害ログは2種類出力されます：

| ログ種別 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | MONITOR | 監視ツールで検知 |
| 障害解析ログ | FATAL/ERROR | クラス名 | 原因究明 |

コードから明示的に出力する場合：
```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

**注意点**:
- `HttpErrorHandler`はHTTPレスポンスハンドラより後ろに配置すること
- `GlobalErrorHandler`はできるだけハンドラキューの先頭に配置すること
- `@OnErrors`で継承関係にある例外を定義する場合はサブクラスを先に記述すること
- `GlobalErrorHandler`は設定による差し替え不可。固有要件がある場合はプロジェクト独自のハンドラを作成すること

参照: component/handlers/handlers-HttpErrorHandler.json, component/handlers/handlers-global-error-handler.json, component/libraries/libraries-failure-log.json, component/libraries/libraries-log.json, processing-pattern/web-application/web-application-forward-error-page.json, processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-on-error.json, component/handlers/handlers-on-errors.json