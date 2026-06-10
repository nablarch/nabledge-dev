**結論**: ウェブアプリケーションのエラー処理は、**HTTPエラー制御ハンドラ（HttpErrorHandler）**が中心となり、例外の種類に応じてログ出力とエラー用HttpResponseの生成を行う。エラー画面への遷移はハンドラまたはアクションのアノテーションで制御し、ログは障害ログ（FATAL/ERROR）またはINFOレベルで出力される。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（HttpErrorHandler）の動作

`nablarch.fw.web.handler.HttpErrorHandler` が後続ハンドラで発生した例外を捕捉し、例外の種類ごとに以下の処理を行う。

| 例外クラス | ログレベル | HTTPステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理するアクションが存在しなかった証跡として記録 |
| `HttpErrorResponse` | なし | レスポンスから取得 | 業務例外のエラーレスポンス（ログ不要） |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern` の正規表現にマッチした場合のみFATAL出力 |
| `StackOverflowError` | FATAL | 500 | データや実装バグに起因する可能性があるため障害として通知 |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外・エラーはすべて障害扱い |

`HttpErrorResponse` の原因例外が `ApplicationException`（バリデーションエラー等）の場合は、エラーメッセージ情報をリクエストスコープの `errors` キーに設定するため、JSPからエラー表示が可能になる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- リクエストスコープへのキー名変更例 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 2. デフォルトエラーページの設定

ステータスコードに対応したデフォルト遷移先は以下のように設定できる（ただし **web.xml の `error-page` 要素での設定を推奨**）。

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

### 3. アクション側でのエラー遷移指定

アクションメソッドに `@OnError` アノテーションを付与することで、例外クラスに対応した遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理は省略
}
```

システム全体で統一したエラーページに遷移させたい場合は、カスタムハンドラを追加して `HttpErrorResponse` をスローする方法を推奨する。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context){
    try{
      return context.handleNext(data);
    } catch (NoDataException e){
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    }
  }
}
```

### 4. 障害ログの出力方針

FATALエラー発生時は、障害ログが2種類出力される。

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | MONITOR | monitor.log（ログ監視ツール用） |
| 障害解析ログ | FATAL / ERROR | クラス名 | app.log（原因特定用） |

`FailureLogUtil.logError()` を使ってアプリケーション側から手動出力することも可能。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

### 5. グローバルエラーハンドラ（GlobalErrorHandler）

`nablarch.fw.handler.GlobalErrorHandler` はハンドラキューの**先頭**に配置し、未捕捉の例外を最終的に捕捉する。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出してログ出力、ServiceErrorを結果として返却 |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力、Result.Errorを返却 |
| 上記以外の例外 | FATALレベルでログ出力、InternalErrorを生成して返却 |

---

**注意点**:
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` と `HTTPアクセスログハンドラ` **より後ろ**に配置する必要がある
- `defaultPages` 機能のみでなく、web.xml の `error-page` 要素でも設定することを推奨（エラー発生箇所によってはウェブサーバのデフォルトページが表示される場合がある）
- `GlobalErrorHandler` はカスタマイズ不可のため、ログレベルを細かく制御したい場合はプロジェクト固有のエラーハンドラを作成すること

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1, libraries-failure-log.json:s3, web-application-feature-details.json:s16, handlers-on-error.json:s3