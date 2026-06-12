これで必要なセクションが揃いました。回答を生成します。

---

**結論**: ウェブアプリケーションでは、**HTTPエラー制御ハンドラ**（`HttpErrorHandler`）が後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とエラーレスポンスを生成する。エラー画面の遷移先は、ハンドラのデフォルト設定・カスタムハンドラ・OnErrorインターセプタの3通りで制御できる。

---

**根拠**:

### 1. HTTPエラー制御ハンドラによる例外処理とログ出力

`nablarch.fw.web.handler.HttpErrorHandler` が後続ハンドラで発生した例外を処理する。例外の種類によってログレベルとHTTPステータスコードが決まる：

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションクラスが存在しない |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` | 業務例外（バリデーションエラー等） |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern`の正規表現がマッチした場合にFATAL |
| `StackOverflowError` | FATAL | 500 | データ・実装バグの可能性 |
| 上記以外 | FATAL | 500 | 予期しない例外 |

`HttpErrorResponse` の原因例外が `ApplicationException`（バリデーションエラー等）の場合は、エラーメッセージ情報を `errors` キーでリクエストスコープに設定し、JSPでエラー表示できるようにする。

### 2. エラー画面（遷移先）の指定方法

**方法①: HTTPエラー制御ハンドラのデフォルトページ設定**（ステータスコードで画面を統一）

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

**方法②: カスタムハンドラで共通エラーページへ遷移**（システム全体で統一する場合に推奨）

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

**方法③: OnErrorインターセプタ**（アクションメソッド単位で指定）

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理は省略
}
```

### 3. グローバルエラーハンドラ

`nablarch.fw.handler.GlobalErrorHandler` はハンドラキューの先頭に配置し、未捕捉の例外・エラーを捕捉してログを出力する：

- `ServiceError`系 → `ServiceError#writeLog`を呼び出し（レベルは実装依存）
- `Result.Error`系 → FATALログ
- `StackOverflowError` → FATALログ → `InternalError`として返却
- `ThreadDeath` → INFOログ → リスロー
- 上記以外の例外 → FATALログ → `InternalError`として返却

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` より後ろ、かつ `HTTPアクセスログハンドラ` より後ろに配置する必要がある。
- `defaultPages` を使う場合、`web.xml` の `error-page` 要素にも同等の設定が必要。設定がないと、エラー発生箇所によってはウェブサーバのデフォルトエラーページが表示される。Nablarchは `web.xml` への設定を推奨している。
- システム全体で共通のエラーページに遷移させたい場合、`OnError` をアクション個別に設定する方法では漏れや指定ミスのリスクがあるため、カスタムハンドラによる集約制御が推奨される。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1, handlers-on-error.json:s3

---