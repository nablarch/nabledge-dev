必要な情報が集まりました。Step 5の回答を生成します。

---

## Step 5–8: 回答生成・検証・出力

収集したセクション内容を元に回答を生成します。

**検証（Step 6）:**
- `HttpErrorHandler`：種類別ログレベル・レスポンスコード → セクション内容に明示あり → supported
- `GlobalErrorHandler`：ハンドラキュー先頭配置推奨 → supported
- `OnError`アノテーション使用例 → supported
- `HttpErrorResponse`でエラーページ遷移 → supported
- 障害ログの`MONITOR`ロガー名 → libraries-failure-logのs1に記載あり → supported

verify_result = PASS

---

**結論**: ウェブアプリケーションでのエラー処理は、主に `HttpErrorHandler`（HTTPエラー制御ハンドラ）と `GlobalErrorHandler`（グローバルエラーハンドラ）の2つのハンドラが担い、例外の種類に応じて自動的にログ出力とエラー画面への遷移を行う仕組みになっている。

**根拠**:

### 1. HTTPエラー制御ハンドラ（HttpErrorHandler）

ウェブアプリケーション専用のエラーハンドラで、後続ハンドラで発生した例外に対してログ出力とHTTPレスポンス生成を自動で行う。

| 例外の種類 | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし | `HttpErrorResponse#getResponse()` に従う |
| `Result.Error` | 設定による（`writeFailureLogPattern`） | `Error#getStatusCode()` に従う |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

**デフォルトのエラーページ設定例:**

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

> ただし、デフォルトのエラーページ設定は `defaultPages` ではなく `web.xml` の `error-page` 要素で行うことが推奨されている。

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージをリクエストスコープのキー `errors` に設定し、JSP側で `${errors}` として参照できるようにする。

### 2. グローバルエラーハンドラ（GlobalErrorHandler）

ハンドラキューの先頭に配置し、未捕捉の例外・エラーを最終的に受け取るハンドラ。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog`でログ出力後、結果として返却 |
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力後、結果として返却 |
| 上記以外 | FATALレベルのログ出力後、`InternalError`を生成して返却 |
| `StackOverflowError` | FATALレベルのログ出力後、`InternalError`を返却 |
| `OutOfMemoryError` | 標準エラー出力に出力後、FATALログを出力し、`InternalError`を返却 |

### 3. アクション単位のエラー遷移先指定（OnErrorインターセプタ）

個別のアクションメソッドで、例外の種類に応じたエラー画面への遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理は省略
}
```

### 4. ハンドラで共通エラーページを定義する方法

システム全体で共通のエラーページへ遷移させたい場合は、個別アクションへのアノテーション設定ではなく、専用のエラー制御ハンドラを作成する。

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

### 5. 障害ログの出力方針

フレームワークは障害ログを2種類に分けて出力する：

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール連携用） | FATAL、ERROR | MONITOR |
| 障害解析ログ（原因調査用） | FATAL、ERROR | クラス名 |

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より後ろ、かつ `HttpAccessLogHandler`（HTTPアクセスログハンドラ）より後ろに配置する必要がある。
- `GlobalErrorHandler` はハンドラキューのできるだけ先頭に配置する。このハンドラより前に配置されたハンドラで例外が発生した場合、ウェブアプリケーションサーバやJVMが処理する。
- このハンドラは設定で実装を切り替えられないため、要件を満たせない場合はプロジェクト固有のハンドラを作成する。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1, handlers-on-error.json:s3, libraries-failure-log.json:s1

---