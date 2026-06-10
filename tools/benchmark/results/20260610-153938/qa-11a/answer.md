**結論**: ウェブアプリケーションでのエラー処理は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）がログ出力とエラー用レスポンス生成を担い、画面遷移先は **OnErrorインターセプタ** またはカスタムエラーハンドラで制御する。

---

**根拠**:

#### 1. HTTPエラー制御ハンドラによるログ出力とレスポンス生成

後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力レベルとHTTPステータスコードを決定する。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しない |
| `HttpErrorResponse` | ログなし | レスポンス内のコード | 業務例外（バリデーション等）のエラー |
| `Result.Error` | 設定による | `getStatusCode()` の値 | `writeFailureLogPattern` で制御 |
| `StackOverflowError` | FATAL | 500 | 障害扱い |
| 上記以外の例外・エラー | FATAL | 500 | 予期しないエラー |

`HttpErrorResponse` の原因が `ApplicationException`（バリデーションエラー等）の場合は、エラーメッセージ情報を `ErrorMessages` に変換してリクエストスコープに `errors` キーで設定する（JSP側で `<n:errors>` タグにより表示できる）。

`Result.Error` のログ出力は `writeFailureLogPattern` に正規表現を設定し、ステータスコードがマッチした場合にFATALレベルで出力する。

#### 2. 障害ログの出力方針

フレームワークの例外ハンドラが自動的に障害ログを出力する。

```properties
# log.properties の設定例
# 障害通知ログ（ログ監視ツールが検知する専用ファイル）
writer.monitorLog.filePath=/var/log/app/monitor.log

# ロガー名 MONITOR: 障害通知ログ（FATAL/ERRORレベル）
loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorLog

# その他はアプリケーションログ
loggers.ROO.nameRegex=.*
loggers.ROO.level=INFO
loggers.ROO.writerNames=appLog
```

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ | FATAL、ERROR | MONITOR |
| 障害解析ログ（スタックトレース含む） | FATAL、ERROR | クラス名 |

#### 3. エラー画面への遷移方法

**方法1: OnErrorインターセプタ（アクション単位）**

アクションのメソッドに `@OnError` アノテーションを設定し、例外クラスと遷移先JSPを紐づける。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**方法2: カスタムエラーハンドラ（システム共通）**

システム全体で遷移先を統一したい場合は、ハンドラキューにカスタムハンドラを追加する。これによりアクションごとへのアノテーション設定漏れを防げる。

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

**方法3: デフォルトページの設定（HttpErrorHandlerのdefaultPages）**

ステータスコードパターンに対してデフォルトのJSPを設定できる。ただし、web.xmlの `error-page` 要素との重複設定が必要になるため、**デフォルトのエラーページ設定はweb.xmlで行うことを推奨**する。

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

**注意点**: `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置する必要がある。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-on-error.json:s3, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1