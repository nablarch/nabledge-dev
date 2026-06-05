これで必要なセクションを読み込みました。回答を生成します。

---

**結論**: ウェブアプリケーションでのエラー処理は主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）が担い、例外の種類に応じてログ出力レベルとHTTPステータスコード・遷移先JSPを決定する。エラー画面の遷移先はデフォルトページ設定・`@OnError`インターセプタ・カスタムハンドラの3つで制御できる。

---

**根拠**:

### 1. HTTPエラー制御ハンドラの動作

`HttpErrorHandler` が後続ハンドラで発生した例外を捕捉し、以下のルールでログ出力とレスポンス生成を行う。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 対応アクションなし |
| `HttpErrorResponse` | 出力なし | レスポンスの値を使用 | 業務例外（バリデーションエラー等） |
| `Result.Error` | 設定による | `getStatusCode()` の値 | `writeFailureLogPattern` 正規表現でFATAL判定 |
| `StackOverflowError` | FATAL | 500 | |
| その他の例外 | FATAL | 500 | |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージをリクエストスコープに `errors` というキーで設定する（JSPで `<n:errors>` タグ等で参照可能）。

### 2. デフォルトエラーページの設定

`HttpErrorHandler` の `defaultPages` プロパティでステータスコードパターンごとに遷移先を設定できる。

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

### 3. アクションレベルでの遷移先指定（`@OnError`）

アクションメソッドに `@OnError` アノテーションを付けることで、例外の種類に応じた遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理は省略
}
```

### 4. ハンドラで共通エラー処理を定義する方法

システム全体で共通のエラーページに遷移させたい場合は、カスタムハンドラを作成する。

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

### 5. 障害ログの出力方針

フレームワークの例外ハンドラが自動的に障害ログを出力する。障害ログは2種類。

| 種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視用） | FATAL, ERROR | `MONITOR` |
| 障害解析ログ（調査用） | FATAL, ERROR | クラス名 |

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置する必要がある（ハンドラキューの順序制約）
- `defaultPages` 機能を使用する場合でも、`web.xml` の `<error-page>` 設定と重複して設定が必要になるため、**デフォルトエラーページは `web.xml` に設定することを推奨**
- `@OnError` は1つの例外に対して1つの遷移先しか指定できない。複数の遷移先が必要な場合はアクション内で `try-catch` と `HttpErrorResponse` を組み合わせて使用する

参照:
- handlers-HttpErrorHandler.json:s4, s5, s6
- web-application-feature-details.json:s16
- web-application-forward-error-page.json:s1, s2
- handlers-on-error.json:s3
- libraries-failure-log.json:s1

---