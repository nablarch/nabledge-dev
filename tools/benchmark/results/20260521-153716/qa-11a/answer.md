セクションを読み込みました。Step 5で回答を生成します。

**結論**: ウェブアプリケーションでのエラー処理は、**HTTPエラー制御ハンドラ**と**グローバルエラーハンドラ**の2つのハンドラが協調して担い、例外の種類に応じてログ出力とエラー画面への遷移を自動的に行います。

---

**根拠**:

### 1. ハンドラキュー上のエラー処理の位置づけ

最小ハンドラ構成では、以下のようにエラー処理ハンドラが2か所に配置されます。

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 2 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力（ハンドラキュー先頭付近） |
| 9 | HTTPエラー制御ハンドラ | 例外種別に応じたログ出力とエラーレスポンス生成 |

---

### 2. HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

後続ハンドラで発生した例外を捕捉し、**例外の種類に応じたログ出力とHTTPレスポンスへの変換**を行います。

| 例外クラス | ログレベル | ステータスコード | 理由 |
|-----------|----------|----------------|------|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションクラスが存在しない |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` | バリデーションなどの業務エラー |
| `Result.Error` | 設定による（`writeFailureLogPattern`） | `Error#getStatusCode()` | 設定した正規表現にマッチすればFATAL |
| `StackOverflowError` | FATAL | 500 | 実装バグに起因する可能性あり |
| 上記以外すべて | FATAL | 500 | 予期しない例外 |

`HttpErrorResponse`の原因例外が`ApplicationException`の場合、エラーメッセージ情報を`ErrorMessages`に変換してリクエストスコープ（デフォルトキー:`errors`）に設定し、JSPでエラー表示できるようにします。

**デフォルトエラーページの設定例（ステータスコードに対応したJSPを指定）**:

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

> ただし、デフォルトページはこの機能ではなく `web.xml` の `error-page` 要素で設定することを推奨します。

---

### 3. グローバルエラーハンドラ（`nablarch.fw.handler.GlobalErrorHandler`）

**ハンドラキューの先頭付近**に配置し、捕捉した例外・エラーに応じてログ出力を行います。

| 例外/エラー | 処理内容 |
|-----------|--------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力、`ServiceError` を返却 |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力、`Result.Error` を返却 |
| `ThreadDeath` | INFOレベルでログ出力後リスロー |
| `StackOverflowError`/`OutOfMemoryError` | FATALレベルでログ出力、`InternalError` を生成して返却 |
| 上記以外 | FATALレベルでログ出力、`InternalError` を生成して返却 |

---

### 4. アクションレベルでのエラー画面遷移指定

アクションのメソッドに`@OnError`アノテーションを付けることで、**例外クラスに対応したエラーページ**を指定できます。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

システム全体で共通のエラーページに遷移させる場合は、個別のアクションにアノテーションを付けるのではなく、**プロジェクト固有のエラー処理ハンドラ**を実装してハンドラキューに追加します。

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

---

### 5. 障害ログの出力方針

フレームワークの例外ハンドラが障害ログを自動出力しますが、アプリケーションで明示的に出力する場合は`FailureLogUtil`を使います。

障害ログは2種類に分かれます：
- **障害通知ログ**（FATAL/ERROR）: `MONITOR`というロガー名で専用ファイルに出力（監視ツールで検知するため）
- **障害解析ログ**（FATAL/ERROR）: クラス名のロガーでアプリケーションログに出力

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler`は`HTTPレスポンスハンドラ`および`HTTPアクセスログハンドラ`より**後ろ**に配置する必要があります。
- `GlobalErrorHandler`は**できるだけハンドラキューの先頭**に配置しないと、手前のハンドラで発生した例外はJVMやアプリケーションサーバーに処理が委ねられます。
- `@OnError`では単一の例外クラスに対して複数の遷移先を指定できないため、その場合はアクション内で`try-catch`を使って`HttpErrorResponse`を生成します。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, web-application-architecture.json:s4, web-application-forward-error-page.json:s1, web-application-forward-error-page.json:s2, web-application-feature-details.json:s16, libraries-failure-log.json:s1

---