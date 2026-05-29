十分な情報が揃いました。Step 5〜8に進みます。

---

**結論**: ウェブアプリケーションのエラー処理は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）と **グローバルエラーハンドラ**（`GlobalErrorHandler`）の2つのハンドラが担い、例外の種類に応じてログ出力レベルとエラー画面への遷移を自動的に制御します。

---

**根拠**:

## ① グローバルエラーハンドラ（先頭配置）

`nablarch.fw.handler.GlobalErrorHandler` はハンドラキューの**できるだけ先頭**に置き、後続で発生した未捕捉例外を全て受け止めます。

| 例外・エラー | ログ | 戻り値 |
|---|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog`（レベルは実装による） | `ServiceError` をそのまま返却 |
| `Result.Error`（サブクラス含む） | FATAL | `Result.Error` を返却 |
| `StackOverflowError` | FATAL | `InternalError` に包んで返却 |
| `OutOfMemoryError` | FATAL（失敗時は標準エラー出力へ） | `InternalError` に包んで返却 |
| 上記以外の例外・エラー | FATAL | `InternalError` に包んで返却 |

## ② HTTPエラー制御ハンドラ（HTTPレスポンス変換担当）

`nablarch.fw.web.handler.HttpErrorHandler` が後続ハンドラの例外をHTTPレスポンスに変換します。

| 例外 | ログ | HTTPステータス |
|---|---|---|
| `HttpErrorResponse`（バリデーションエラーなどの業務例外） | **ログ出力なし** | `HttpErrorResponse#getResponse()` のステータス |
| `NoMoreHandlerException` | INFO | 404 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因が `ApplicationException` の場合、エラーメッセージ情報が `ErrorMessages` としてリクエストスコープ（デフォルトキー: `errors`）に設定され、JSP側でエラー表示に使えます。

`Result.Error` については、`writeFailureLogPattern` に設定した正規表現とステータスコードがマッチした場合のみ FATAL ログを出力します。

## ③ デフォルトエラーページの設定

`defaultPages` プロパティでステータスコードのパターンに対するJSPを設定できますが、**web.xmlへの設定が推奨**です。

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

## ④ アクション単位のエラー遷移（OnErrorインターセプタ）

アクションメソッドに `@OnError` を付与することで、例外クラスごとの遷移先JSPを指定できます。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

## ⑤ システム共通のエラーページ（カスタムハンドラ）

`@OnError` はメソッドごとの設定なのでシステム全体の統一には向きません。カスタムハンドラで共通化する方法が推奨されます。

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

## ⑥ 障害ログの出力

フレームワークの例外ハンドラが自動的に出力するほか、アプリケーション側で明示的に出力する場合は `FailureLogUtil` を使用します。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

障害ログは2種類に分かれています：

| ログ種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール用） | FATAL/ERROR | `MONITOR` |
| 障害解析ログ（原因調査用） | FATAL/ERROR | クラス名 |

---

**注意点**:
- `GlobalErrorHandler` より手前のハンドラで例外が発生した場合は、APサーバやJVMの例外処理に委ねられる
- `HttpErrorResponse` はログ出力なしのため、業務例外のトレースが必要な場合は別途ログを仕込む必要がある

参照: `handlers-HttpErrorHandler.json:s4`, `handlers-HttpErrorHandler.json:s5`, `handlers-HttpErrorHandler.json:s6`, `handlers-global-error-handler.json:s3`, `handlers-global-error-handler.json:s4`, `libraries-failure-log.json:s1`, `libraries-failure-log.json:s3`, `libraries-failure-log.json:s4`, `web-application-forward-error-page.json:s1`, `handlers-on-error.json:s3`

---