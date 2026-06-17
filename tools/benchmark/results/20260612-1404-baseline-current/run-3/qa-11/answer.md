**結論**: ウェブアプリケーションでのエラー処理は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）と **グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担い、例外の種類に応じたログ出力とエラー画面へのレスポンス生成を自動的に行う。

---

**根拠**:

### ハンドラキューにおける位置

最小ハンドラ構成では、エラー処理に関わるハンドラが2か所に配置される：

| No. | ハンドラ | 例外処理 |
|-----|----------|----------|
| 2 | グローバルエラーハンドラ | 実行時例外・エラーをログ出力 |
| 9 | HTTPエラー制御ハンドラ | 例外の種類に応じたログ出力とレスポンス生成 |

---

### HTTPエラー制御ハンドラ（`HttpErrorHandler`）の動作

後続ハンドラで発生した例外をキャッチし、例外の種類に応じてログとレスポンスを決定する：

| 例外クラス | ログレベル | レスポンス | 備考 |
|-----------|-----------|----------|------|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しない場合 |
| `HttpErrorResponse` | ログなし | `getResponse()` の内容 | 業務例外（バリデーションエラー等）の場合はログ不要。原因が `ApplicationException` の場合はエラーメッセージをリクエストスコープに `errors` キーで設定 |
| `Result.Error` | FATAL（設定次第） | `getStatusCode()` の値 | `writeFailureLogPattern` の正規表現にマッチした場合のみ FATAL 出力 |
| `StackOverflowError` | FATAL | 500 | 実装バグに起因する可能性があるため障害扱い |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外は障害扱い |

**デフォルトエラーページの設定例**（`defaultPages`）：

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

> デフォルトのエラーページ設定は、この機能よりも `web.xml` の `error-page` 要素で行うことを推奨する（ウェブサーバのデフォルトエラーページが表示される場合があるため）。

---

### グローバルエラーハンドラ（`GlobalErrorHandler`）の動作

ハンドラキューの先頭付近に配置し、HttpErrorHandler より上位で未捕捉の例外・エラーを処理する：

| 例外・エラークラス | 処理内容 |
|-----------------|--------|
| `ServiceError`（サブクラス含む） | `writeLog()` を呼び出してログ出力（ログレベルは実装クラスによる） |
| `Result.Error`（サブクラス含む） | FATAL ログ出力後、`Result.Error` を返却 |
| `ThreadDeath` | INFO ログ後、リスロー |
| `StackOverflowError` | FATAL ログ後、`InternalError` を返却 |
| `OutOfMemoryError` | 標準エラー出力後に FATAL ログ、`InternalError` を返却 |
| 上記以外の例外・エラー | FATAL ログ後、`InternalError` を返却 |

---

### エラー画面への遷移指定方法

**個別アクションへの指定**（`@OnError` インターセプタ）：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**システム共通のエラー画面**をまとめて設定したい場合は、独自のハンドラを作成してハンドラキューに追加する（個別アクションへのアノテーション設定では漏れや指定ミスが発生するリスクがある）：

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

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置すること（前に置くと生成した HttpResponse が正しく処理・ログ記録されない）。
- `GlobalErrorHandler` は設定による実装の切り替えができないため、ログレベルを細かく変えたい場合などはプロジェクト固有のハンドラを作成すること。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, web-application-architecture.json:s4, web-application-forward-error-page.json:s1, handlers-on-error.json:s3