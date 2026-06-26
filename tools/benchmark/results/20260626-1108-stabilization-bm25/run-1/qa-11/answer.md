**結論**

ウェブアプリケーションのエラー処理は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）がハンドラキュー上で例外を捕捉し、例外の種類に応じたログ出力とエラー画面へのレスポンス生成を行う仕組みになっています。エラー画面への遷移先は `@OnError` インターセプタやハンドラで定義します。

---

**根拠**

## 1. HTTPエラー制御ハンドラによる例外処理とログ出力

`HttpErrorHandler` がハンドラキューの後続で発生した例外を捕捉し、例外の種類に応じて以下のように処理します。

| 例外クラス | ログレベル | HTTPステータス | 補足 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しない場合 |
| `HttpErrorResponse` | ログ出力なし | `HttpErrorResponse` のステータスコード | 業務例外（バリデーションエラーなど）のため出力しない |
| `Result.Error` | 設定による（FATAL） | `Error#getStatusCode()` | `writeFailureLogPattern` に設定した正規表現がステータスコードにマッチした場合にFATALログ |
| `StackOverflowError` | FATAL | 500 | データや実装バグに起因するため障害通知 |
| 上記以外 | FATAL | 500 | 予期しない例外として障害扱い |

`HttpErrorResponse` の原因例外が `ApplicationException`（バリデーションエラーなど）の場合は、ログ出力を行わず、メッセージ情報を `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に設定します。これによりViewでエラーメッセージを表示できます。

```xml
<!-- キー名を変更したい場合のコンポーネント設定 -->
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

## 2. エラー画面への遷移先の指定方法

遷移先の指定には3つの方法があります。

**① アクションメソッドの `@OnError` アノテーション（個別指定）**

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**② カスタムハンドラによる一括定義（システム共通のエラーページ）**

全アクションに共通の遷移先を設定する場合は、個別のアノテーション指定ではなくハンドラで定義します。漏れや指定ミスを防止できます。

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context) {
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    } catch (OptimisticLockException e) {
      throw new HttpErrorResponse(400, "/WEB-INF/view/common/errorPages/optimisticLockError.jsp", e);
    }
  }
}
```

**③ `HttpErrorHandler` のデフォルトページ設定（ステータスコード別）**

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

> ただし、③よりも `web.xml` の `<error-page>` 要素で設定することが推奨されています。`web.xml` に設定しない場合、エラー発生箇所によってはウェブサーバのデフォルトエラーページが表示される可能性があります。

## 3. 障害ログの出力方針

HTTPエラー制御ハンドラがFATALログとして出力する障害ログは、以下の方針で出力されます。

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | MONITOR | 監視専用ファイル（monitor.log） |
| 障害解析ログ | FATAL / ERROR | クラス名 | アプリケーションログ（app.log） |

`app-log.properties` でデフォルトの障害コードとメッセージを設定します。

```properties
failureLogFormatter.defaultFailureCode=MSG99999
failureLogFormatter.defaultMessage=an unexpected exception occurred.
failureLogFormatter.notificationFormat=fail_code = [$failureCode$] $message$
failureLogFormatter.analysisFormat=fail_code = [$failureCode$] $message$\nInput Data :\n$data$
```

アプリケーションから明示的に障害ログを出力する場合は `FailureLogUtil` を使用します。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**

- `@OnError` は1つの例外クラスに対して1つの遷移先しか指定できません。同じ例外クラスで複数の遷移先が必要な場合は、アクションメソッド内で `try-catch` を使用して `HttpErrorResponse` をスローしてください。
- `HttpErrorHandler` のデフォルトページ設定を使う場合も、`web.xml` 側への設定が必要です（二重設定になりますが必須）。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1, web-application-forward-error-page.json:s2, libraries-failure-log.json:s1, libraries-failure-log.json:s3, handlers-on-error.json:s3