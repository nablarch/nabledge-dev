Step 5: 回答を生成します。

**結論**: ウェブアプリケーションのエラーハンドリングは、主に**HTTPエラー制御ハンドラ**（`HttpErrorHandler`）と**グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担い、例外の種類に応じてログ出力レベルとエラー画面への遷移を自動制御する。

---

**根拠**:

### ログ出力の仕組み（HTTPエラー制御ハンドラ）

`HttpErrorHandler` は後続ハンドラで発生した例外を捕捉し、種類に応じてログレベルとレスポンスを決定する。

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし | レスポンスに従う |
| `Result.Error` | `writeFailureLogPattern` に依存（マッチ時FATAL） | `Error#getStatusCode()` に従う |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` は業務例外（バリデーションエラー等）を意味するため、ログ出力は行わない。`Result.Error` は `writeFailureLogPattern` プロパティ（正規表現）がステータスコードにマッチした場合のみFATALログを出力する。

### グローバルエラーハンドラ（ハンドラキュー先頭配置）

`GlobalErrorHandler` はできるだけハンドラキューの先頭に配置し、最上位の例外を捕捉する。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError` | `ServiceError#writeLog` でログ出力（レベルは実装クラス依存） |
| `Result.Error` | FATALログ出力後、Result.Errorを返却 |
| 上記以外 | FATALログ出力後、`InternalError` に包んで返却 |

### エラー画面への遷移方法（3種類）

**① HTTPエラー制御ハンドラのデフォルトページ設定**（ステータスコード単位）:

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

> 注意：デフォルトページの設定は `defaultPages` より `web.xml` の `<error-page>` 要素での設定を推奨。

**② カスタムエラー処理ハンドラ**（例外クラス単位で共通遷移先を制御）:

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

**③ `@OnError` インターセプタ**（アクションメソッド単位）:

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

エラー時の遷移先画面でデータ取得が必要な場合は、`path` に `forward://メソッド名` を指定して内部フォワードする。

---

**注意点**:
- `HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージはリクエストスコープの `errors` キー（変更可）に自動設定される。JSP側でこの情報を参照してエラーメッセージを表示できる。
- システム全体で共通エラーページにしたい場合は、個別アクションへの `@OnError` 設定より、カスタムエラー処理ハンドラの追加を推奨（漏れや指定ミスを防ぐため）。
- `GlobalErrorHandler` は設定で実装を切り替えられないため、ログレベルを細かく制御したい場合はプロジェクト固有のエラー処理ハンドラを作成する。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1, handlers-on-error.json:s3

---