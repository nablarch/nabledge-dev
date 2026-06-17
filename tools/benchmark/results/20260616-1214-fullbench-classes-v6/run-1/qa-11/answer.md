**結論**: ウェブアプリケーションのエラー処理は、**HTTPエラー制御ハンドラ（HttpErrorHandler）** が例外の種類に応じたログ出力とHTTPレスポンス（エラー画面）生成を一元的に担う。個別のアクションへの遷移先制御には `@OnError` インターセプタ、未捕捉例外の処理には **グローバルエラーハンドラ**、障害ログ出力には専用の障害ログ機能が使われる多層構造になっている。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（HttpErrorHandler）

後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とHTTPレスポンスを生成する。

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | `writeFailureLogPattern` に一致すれば FATAL | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外すべて | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージを `ErrorMessages` に変換してリクエストスコープの `errors` キーに自動設定する（JSPで `<n:errors>` タグを使って表示可能）。

ステータスコードに対応するデフォルトのエラーページはコンポーネント設定で指定する：

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

### 2. グローバルエラーハンドラ（GlobalErrorHandler）

ハンドラキューの先頭近くに配置し、未捕捉の例外・エラーを捕捉してログ出力と結果返却を行う。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出しログ出力後、`ServiceError` を返却 |
| `Result.Error`（サブクラス含む） | FATAL レベルのログ出力後、`Result.Error` を返却 |
| 上記以外 | FATAL レベルのログ出力後、`InternalError` を生成して返却 |

### 3. アクション単位のエラー画面遷移（OnError インターセプタ）

業務アクションのメソッドに `@OnError` アノテーションを設定し、例外発生時の遷移先を指定する：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

エラー時の遷移先画面でデータ表示が必要な場合は、内部フォワードを使う：

```java
@InjectForm(form = PersonForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://initializeRegisterPage")
public HttpResponse confirmForRegister(HttpRequest request, ExecutionContext context) {
    PersonForm form = context.getRequestScopedVar("form");
    return new HttpResponse("/WEB-INF/view/person/confirmForRegister.jsp");
}

public HttpResponse initializeRegisterPage(HttpRequest request, ExecutionContext context) {
    // 画面表示データをデータベースなどから取得し、リクエストスコープに設定する
    return new HttpResponse("/WEB-INF/view/person/inputForRegister.jsp");
}
```

### 4. システム共通のエラーページ制御（カスタムハンドラ）

複数アクションに同じ遷移先を設定するよりも、カスタムハンドラをハンドラキューに追加する方が確実：

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

### 5. 障害ログの出力

障害ログは2種類に分けて出力される：

| ログの種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | MONITOR | ログ監視ツールによる障害検知専用ファイル |
| 障害解析ログ | FATAL / ERROR | クラス名 | アプリケーションログ全体 |

フレームワークの例外ハンドラが自動出力する。アプリケーション側で出力する場合は `FailureLogUtil` を使う：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より後ろに配置すること（生成した `HttpResponse` を `HttpResponseHandler` が処理するため）
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること
- `HttpErrorHandler` の `defaultPages` を使う場合、`web.xml` の `error-page` 要素も設定することを推奨（設定がないとウェブサーバのデフォルトエラーページが表示される場合がある）

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-on-error.json:s3, handlers-on-error.json:s4, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1, libraries-failure-log.json:s3