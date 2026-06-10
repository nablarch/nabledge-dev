**結論**: ウェブアプリケーションのエラー処理は、主に「HTTPエラー制御ハンドラ (`HttpErrorHandler`)」が担当し、例外の種類に応じてログレベルとHTTPステータスコードを決定してエラー画面へ誘導する。ログ出力は「障害通知ログ」（監視用）と「障害解析ログ」（解析用）の2種類が使い分けられる。

---

**根拠**:

### 1. 例外種別ごとのログ出力とレスポンス（HttpErrorHandler）

後続ハンドラで発生した例外は、`HttpErrorHandler` が種別ごとに以下の処理を行う：

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` の内容 |
| `Result.Error` | `writeFailureLogPattern` の設定による（FATALの場合あり） | `Error#getStatusCode()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外/エラー | FATAL | 500 |

`writeFailureLogPattern` は正規表現で指定し、マッチしたステータスコードの場合にFATALログを出力する。

### 2. エラー画面の表示（HttpResponseHandler + defaultPages）

`HttpResponseHandler` は、ステータスコードが **400以上** の場合にエラー画面を表示する。表示するページは `HttpErrorHandler` の `defaultPages` プロパティで設定する：

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

> 上記設定では `web.xml` の `<error-page>` 設定も合わせて必要。推奨はデフォルトエラーページを `web.xml` 側で設定すること。

### 3. バリデーションエラー時の画面遷移（@OnError）

業務アクションのメソッドに `@OnError` アノテーションを付けることで、特定の例外発生時の遷移先JSPを指定できる：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

`ApplicationException` が `HttpErrorResponse` にラップされている場合は、エラーメッセージ情報が `ErrorMessages` に変換されてリクエストスコープの `errors` キーにセットされる（View側で参照可能）。

### 4. 障害ログの2種類の出力

フレームワークは例外発生時に以下2種類の障害ログを出力する：

| ログ種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | `MONITOR` | 監視専用ファイル（監視ツールが検知） |
| 障害解析ログ | FATAL / ERROR | クラス名 | アプリケーションログファイル |

設定例（`log.properties`）：
```properties
loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorLog

loggers.ROO.nameRegex=.*
loggers.ROO.level=INFO
loggers.ROO.writerNames=appLog
```

アプリケーションから直接障害ログを出力する場合は `FailureLogUtil` を使用する：

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

---

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（レスポンス生成）および `HTTPアクセスログハンドラ` より **後ろ** に配置する必要がある（生成したレスポンスをそれらが処理するため）
- `GlobalErrorHandler` はハンドラキューの **先頭** に配置すること（先頭より手前で例外が発生するとJVMやアプリサーバが処理することになる）
- `HttpResponseHandler` 内で致命的エラーが発生した場合は、ステータスコード500の固定HTMLが返される（設定で変更不可）

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, libraries-failure-log.json:s1, libraries-failure-log.json:s3, handlers-global-error-handler.json:s4, handlers-on-error.json:s3, handlers-http-response-handler.json:s4, handlers-http-response-handler.json:s8