答えを生成します。

---

**結論**: ウェブアプリケーションのエラーハンドリングは、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）と **グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担う。前者はエラー画面表示とログ出力を例外種別ごとに制御し、後者はすべての未捕捉例外を最終的に補足してログを出力する。

---

**根拠**:

## HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

後続ハンドラで発生した例外を捕捉し、**ログ出力とエラー用レスポンスへの変換**を行う。例外の種類によって処理が異なる：

| 例外クラス | ログレベル | HTTPステータス | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | アクションクラスが存在しない |
| `HttpErrorResponse` | なし | `HttpErrorResponse#getResponse()` | バリデーション等の業務例外（`ApplicationException`）が原因の場合、`ErrorMessages`をリクエストスコープの`errors`キーに設定 |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern`に設定した正規表現がステータスコードにマッチした場合のみFATAL |
| `StackOverflowError` | FATAL | 500 | - |
| 上記以外の例外・エラー | FATAL | 500 | - |

### デフォルトのエラーページ設定

`defaultPages`プロパティで、ステータスコードに対応したデフォルトのJSPページを設定できる：

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

> ただし、デフォルトのエラーページは `web.xml` の `error-page` 要素で設定することが推奨されている。

---

## グローバルエラーハンドラ（`nablarch.fw.handler.GlobalErrorHandler`）

未捕捉例外を捕捉してログ出力と結果返却を行う。ハンドラキューの**先頭に配置**することが推奨される：

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog`を呼び出してログ出力。ログレベルは実装クラスによる |
| `Result.Error`（サブクラス含む） | FATALレベルのログを出力して`Result.Error`を返却 |
| 上記以外の例外 | FATALレベルのログを出力して`InternalError`を生成・返却 |
| `StackOverflowError` | FATALレベルのログを出力して`InternalError`を生成・返却 |
| `ThreadDeath`、`VirtualMachineError` | リスロー |

このハンドラは設定による切り替えができないため、ログレベルの細かい制御など要件を満たせない場合はプロジェクト固有のエラー処理ハンドラを作成する。

---

## アクション・ハンドラでのエラー画面遷移の制御

エラー時の遷移先の指定方法は3つある：

1. **`@OnError` アノテーション**（アクションメソッドごとに設定）：
```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

2. **共通ハンドラで例外クラスに対応したページへ遷移**（システム全体の共通エラーページに使用）：
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

3. **`HttpErrorHandler`の`defaultPages`**（ステータスコードベースのデフォルトページ設定）

---

**注意点**:
- `HttpErrorResponse`（業務例外起因）はログが出力されない設計になっている
- `HttpErrorHandler`は`HTTPレスポンスハンドラ`・`HTTPアクセスログハンドラ`より後ろに配置する必要がある
- `GlobalErrorHandler`は設定で実装を切り替えられないため、カスタマイズが必要な場合は独自ハンドラを作成する

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, web-application-forward-error-page.json:s1, handlers-on-error.json:s3

---