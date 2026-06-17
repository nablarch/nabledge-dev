**結論**: ウェブアプリケーションでのエラー処理は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）が担っており、後続ハンドラで発生した例外の種類に応じてログ出力レベルとHTTPステータスコードを自動的に決定し、エラー画面への遷移も設定により制御できる。

---

**根拠**:

#### 1. 例外の種類に応じたログ出力とレスポンス生成（HttpErrorHandler）

`HttpErrorHandler` は後続ハンドラで発生した例外をキャッチし、以下のように処理する：

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `HttpErrorResponse` のレスポンスを使用 |
| `Result.Error` | `writeFailureLogPattern` の設定による | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

業務例外（`ApplicationException`）を原因に持つ `HttpErrorResponse` の場合は、ログ出力を行わず、エラーメッセージを `ErrorMessages` に変換してリクエストスコープに `errors` キーで設定する。これにより View 側でエラーメッセージを表示できる。

#### 2. グローバルエラーハンドラ（GlobalErrorHandler）

`GlobalErrorHandler` は未捕捉の例外をすべて処理する最後の砦として、**ハンドラキューの先頭付近**に配置する：

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出す |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| それ以外の例外 | FATALレベルでログ出力 + `InternalError` を生成して返却 |

#### 3. エラー時の画面遷移の指定方法

エラー時の遷移先は 3 つの方法で指定できる：

**① OnErrorインターセプタ**（アクション単位）

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**② カスタムハンドラ**（システム共通）

複数のアクションで同じエラー画面に遷移させたい場合、ハンドラで一括制御するのが推奨される：

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

**③ HttpErrorHandlerのデフォルトページ設定**（ステータスコード対応）

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

#### 4. 障害ログの出力方針

障害ログは 2 種類に分けて出力される：

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | `MONITOR` | 監視専用ファイル |
| 障害解析ログ | FATAL / ERROR | クラス名 | アプリケーションログ |

`log.properties` の設定例：
```properties
# 障害通知ログの出力設定
loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorLog
```

アプリケーション側で障害ログを出力する場合は `FailureLogUtil` を使用する：
```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler` は **HTTPレスポンスハンドラより後ろ**、かつ **HTTPアクセスログハンドラより後ろ**に配置する必要がある（配置順を誤るとエラーレスポンスやアクセスログが正しく処理されない）
- `HttpErrorHandler` の `defaultPages` 機能を使う場合は、`web.xml` の `error-page` 要素も合わせて設定しないと、エラー発生箇所によってはサーバのデフォルトエラーページが表示されることがある。そのため **`web.xml` への設定を推奨** している
- `GlobalErrorHandler` は設定で実装を切り替えできないため、ログレベルを細かく制御したい場合はプロジェクト固有のハンドラを作成する必要がある

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s3, handlers-global-error-handler.json:s4, web-application-forward-error-page.json:s1, handlers-on-error.json:s3, libraries-failure-log.json:s1, libraries-failure-log.json:s3, web-application-feature-details.json:s16