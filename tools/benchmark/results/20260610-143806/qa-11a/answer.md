**結論**: ウェブアプリケーションのエラー処理は、`HttpErrorHandler`（HTTPエラー制御ハンドラ）が例外の種類に応じてログ出力とエラー画面レスポンスを生成し、`GlobalErrorHandler`（グローバルエラーハンドラ）が未捕捉の例外を最上位で受け取る2層構造になっている。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

後続ハンドラで発生した例外を捕捉し、**例外の種類に応じてログ出力とHTTPレスポンスを生成**する。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションクラスが存在しない |
| `HttpErrorResponse` | ログなし | `getResponse()` の値 | バリデーションなど業務例外起因の意図的なエラー応答 |
| `Result.Error` | 設定による | `getStatusCode()` の値 | `writeFailureLogPattern` の正規表現にマッチした場合は FATAL |
| `StackOverflowError` | FATAL | 500 | データや実装バグ起因の可能性があり障害扱い |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外・エラーは障害扱い |

**HttpErrorResponseとApplicationExceptionの連携**: `HttpErrorResponse`の原因例外が`ApplicationException`の場合、バリデーションエラーメッセージをViewで扱えるよう、メッセージ情報を`ErrorMessages`に変換してリクエストスコープ（デフォルトキー: `errors`）に設定する。

**デフォルトエラーページの設定**: `defaultPages`プロパティにステータスコードのパターンと遷移先JSPを設定できる。

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

> デフォルトのエラーページ設定は、`web.xml`の`error-page`要素で行うことを推奨（本機能と重複するとJSP設定が二重に必要になる）。

---

### 2. グローバルエラーハンドラ（`nablarch.fw.handler.GlobalErrorHandler`）

ハンドラキューの**先頭付近**に配置し、未捕捉の例外・エラーを最上位で処理する。

| 例外・エラー | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `writeLog`を呼び出し（ログレベルは実装クラスによる）、`ServiceError`を返却 |
| `Result.Error`（サブクラス含む） | FATALログ出力後、`Result.Error`を返却 |
| `StackOverflowError` | FATALログ出力後、`InternalError`を生成して返却 |
| `OutOfMemoryError` | 標準エラー出力に出力後、FATALログ出力し、`InternalError`を返却 |
| 上記以外の例外 | FATALログ出力後、`InternalError`を生成して返却 |

> ログレベルを細かく切り替えたい場合は、`GlobalErrorHandler`を使わずプロジェクト固有のエラー処理ハンドラを新たに作成すること。

---

### 3. 障害ログの出力（`FailureLogUtil`）

障害ログは**2種類**に分類して出力する。

| ログの種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL、ERROR | `MONITOR` | ログ監視ツールによる障害検知用の専用ファイルに出力 |
| 障害解析ログ | FATAL、ERROR | クラス名 | アプリケーションログに出力、スタックトレース含む |

アプリケーションで障害ログを直接出力する場合は`FailureLogUtil`を使用する:

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

### 4. エラー画面遷移の指定方法

**アクション単位の指定（`@OnError`インターセプタ）**:

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**システム全体で共通のエラーページに遷移させる場合**: 個別アノテーションではなく、**エラー制御ハンドラ**をハンドラキューに追加して対応するのが推奨パターン（漏れや指定ミスを防ぐため）:

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

**注意点**: `HttpErrorHandler`はHTTPレスポンスハンドラおよびHTTPアクセスログハンドラより**後ろ**に配置する必要がある（生成したエラー用`HttpResponse`をこれらのハンドラが処理するため）。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, handlers-on-error.json:s3, libraries-failure-log.json:s1, libraries-failure-log.json:s3, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1