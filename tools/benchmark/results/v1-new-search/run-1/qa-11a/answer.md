**結論**: ウェブアプリケーションのエラー処理は、主に「**HTTPエラー制御ハンドラ**」と「**グローバルエラーハンドラ**」の2段構えで行われる。例外の種類に応じてログレベル（INFO/FATAL）を自動選択し、対応するHTTPレスポンス（エラー画面）を生成する。

**根拠**:

### 1. HTTPエラー制御ハンドラ（ウェブアプリ専用）

クラス名: `nablarch.fw.web.handler.HttpErrorHandler`

後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とエラー用レスポンスを生成する。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | ハンドラ不在を証跡として記録 |
| `HttpErrorResponse` | なし | レスポンス内のコード | 業務エラー（バリデーション等）は通常ログ不要 |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern`の正規表現がマッチした場合にFATAL |
| `StackOverflowError` | FATAL | 500 | 障害扱い |
| その他の例外・エラー | FATAL | 500 | 予期しないエラーは障害扱い |

`HttpErrorResponse`の原因例外が`ApplicationException`の場合、JSPでエラーメッセージを表示できるよう`ErrorMessages`がリクエストスコープの`errors`キーに自動設定される。

**デフォルトエラーページの設定**（ステータスコードベース）:
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
> なお、Nablarchはデフォルトページの設定を`HttpErrorHandler`ではなく`web.xml`の`error-page`要素で行うことを推奨している。

### 2. グローバルエラーハンドラ（全処理方式共通）

クラス名: `nablarch.fw.handler.GlobalErrorHandler`

ハンドラキューの先頭付近に配置し、未捕捉の例外・エラーを最終的に捕捉する。

| 例外/エラー | 処理内容 |
|---|---|
| `ServiceError` | `ServiceError#writeLog`を呼び出す（ログレベルは実装クラスによる） |
| `Result.Error` | FATALログ出力後、`Result.Error`を返却 |
| その他の例外 | FATALログ出力後、`InternalError`を生成して返却 |
| `StackOverflowError` | FATALログ出力後、`InternalError`を返却 |
| `OutOfMemoryError` | 標準エラー出力に出力後、FATALログ出力、`InternalError`を返却 |

### 3. アクションレベルでのエラー画面指定

業務アクションのメソッドに`@OnError`アノテーションを付けることで、特定例外発生時の遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

### 4. システム横断のエラー画面制御（カスタムハンドラ）

特定の例外に対してシステム全体で共通のエラーページに遷移させる場合は、カスタムハンドラをハンドラキューに追加する。

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

**注意点**:
- `グローバルエラーハンドラ`はハンドラキューの**先頭**に配置すること（それより前で発生した例外はアプリケーションサーバが処理する）
- `HTTPエラー制御ハンドラ`は`HTTPレスポンスハンドラ`および`HTTPアクセスログハンドラ`より**後ろ**に配置すること
- `OnErrorインターセプタ`では単一例外に対して1つの遷移先しか指定できない。複数の遷移先が必要な場合はアクション内で`HttpErrorResponse`を直接生成する

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, web-application-forward-error-page.json:s1, handlers-on-error.json:s3, web-application-feature-details.json:s16