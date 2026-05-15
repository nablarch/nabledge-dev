**結論**: Nablarchのエラー処理は「ハンドラによる例外捕捉 → ログ出力 → エラー画面遷移」の3層構造で実現される。処理方式（Web/バッチ等）によって使用するハンドラが異なる。

## 1. グローバルエラーハンドラ（全処理方式共通）

`nablarch.fw.handler.GlobalErrorHandler` がハンドラキューの先頭近くに配置され、後続ハンドラの未捕捉例外を捕捉してログを出力する。

| 例外/エラー | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | ServiceError実装クラスによる | `writeLog()` 呼び出し後、結果として返却 |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後、結果として返却 |
| `ThreadDeath` | INFO | ログ出力後リスロー |
| `StackOverflowError` | FATAL | ログ出力後 `InternalError` を生成して返却 |
| `OutOfMemoryError` | FATAL | 標準エラー出力へ出力後、FATALログ、`InternalError` を返却 |
| 上記以外 | FATAL | ログ出力後 `InternalError` を生成して返却 |

## 2. HTTPエラー制御ハンドラ（Webアプリ専用）

`nablarch.fw.web.handler.HttpErrorHandler` が例外をHTTPレスポンスに変換する。

| 例外 | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `getResponse()` の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外 | FATAL | 500 |

- `HttpErrorResponse` の原因が `ApplicationException` の場合、バリデーションエラーメッセージを `ErrorMessages` に変換してリクエストスコープ（キー: `errors`）にセットし、Viewで参照できるようにする。

エラー画面のデフォルトページ設定例:
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

推奨はweb.xml側でのエラーページ設定。

## 3. アクションメソッド単位のエラー遷移（OnErrorインターセプタ）

`@OnError` アノテーションでアクションメソッドごとにエラー遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

## 4. システム共通エラー遷移ハンドラ（カスタム実装）

全画面で統一したエラーページに遷移させたい場合は、独自のハンドラを作成して追加する（`@OnError` の漏れを防ぐため推奨）。

## 5. 障害ログの出力（FailureLogUtil）

障害ログは「障害通知ログ（監視用、ロガー名: MONITOR）」と「障害解析ログ（分析用、クラス名）」の2種類。

```java
FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
```

バッチ処理で後続継続せず終了する場合は例外ハンドラに委譲:
```java
throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
```

**注意点**:
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること
- `HttpErrorHandler` は `HTTPレスポンスハンドラ` および `HTTPアクセスログハンドラ` より後ろに配置する必要がある
- `GlobalErrorHandler` はカスタマイズ不可。ログレベルの細かい制御など要件を満たせない場合はプロジェクト固有のエラー処理ハンドラを作成すること
- 障害ログのデフォルト障害コード（`failureLogFormatter.defaultFailureCode`）は必須設定項目
- セキュリティ要件で個人情報・機密情報の出力が許されない場合は `FailureLogFormatter` をカスタマイズしてマスク処理を実装すること

参照: handlers-global-error-handler.json#s4, handlers-HttpErrorHandler.json#s4, handlers-HttpErrorHandler.json#s6, libraries-failure-log.json#s1, libraries-failure-log.json#s3, handlers-on-error.json#s3, web-application-forward-error-page.json#s1