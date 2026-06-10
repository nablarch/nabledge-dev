**結論**: ウェブアプリケーションでは、`HttpErrorHandler`（HTTPエラー制御ハンドラ）が後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログレベルとHTTPレスポンスを決定します。エラー画面は`defaultPages`の設定または`@OnError`アノテーションで指定し、ログは障害通知ログ（MONITORロガー）と障害解析ログ（アプリログ）の2系統に分離して出力されます。

---

**根拠**:

### 1. 例外の種類に応じたログ出力とレスポンス（HttpErrorHandler）

`HttpErrorHandler`は後続ハンドラで発生した例外をキャッチし、以下のように処理します。

| 例外クラス | ログ出力 | HTTPステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし（業務例外のため） | `HttpErrorResponse#getResponse()` のコード |
| `Result.Error` | `writeFailureLogPattern`に依存（マッチ時FATAL） | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse`の原因例外が`ApplicationException`の場合は、エラーメッセージを`ErrorMessages`に変換してリクエストスコープの`errors`キーにセットします（キー名はコンポーネント設定で変更可）。

### 2. エラー画面（デフォルトページ）の設定

`defaultPages`プロパティでステータスコードごとのエラーページを設定します。

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

> **注意**: この機能を使う場合は`web.xml`の`error-page`要素にも同様の設定が必要です。設定がないと、エラー発生場所によってはウェブサーバのデフォルトエラーページが表示されます。公式にはデフォルトエラーページの設定は`web.xml`側で行うことが推奨されています。

### 3. アクションメソッドごとのエラー遷移（@OnError）

個々のアクションメソッドには`@OnError`アノテーションで遷移先を指定できます。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

`type`には`RuntimeException`およびそのサブクラスを指定できます。サブクラスも処理対象となります。

システム全体で共通のエラーページに遷移させたい場合は、個別のアノテーションより以下のような共通ハンドラで制御する方が漏れが少なくなります。

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

### 4. 障害ログの出力方針（2系統分離）

エラー発生時のログは通知用と解析用の2系統に分離して出力されます。

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL、ERROR | MONITOR | monitor.log（監視ツールで監視） |
| 障害解析ログ | FATAL、ERROR | クラス名 | app.log（全体アプリログ） |

フレームワークの方針として、**1件の障害に対して1件の障害ログ**を出力します。障害連鎖で発生した2件目以降の例外はWARNレベルで出力されます。

ログレベルの意味：
- **FATAL**: アプリ継続不可能。即通報・即対応が必要
- **ERROR**: 継続に支障あり。監視必須だがFATALほど緊急ではない
- **INFO**: 認可チェックエラーやURLパラメータ改竄エラーなど、アプリレベルのエラー検知に使用

アプリコードで障害ログを明示的に出力する場合は`FailureLogUtil`を使います。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler`の`defaultPages`機能を使う場合、`web.xml`の`error-page`設定との併用が必要。未設定だとウェブサーバのデフォルトページが表示される場合があります。
- フレームワークは「例外を処理する単一のハンドラ」で障害通知ログを出力する方針のため、独自ハンドラを追加する場合はログの重複出力に注意してください。

参照: `handlers-HttpErrorHandler.json:s4`, `handlers-HttpErrorHandler.json:s5`, `handlers-HttpErrorHandler.json:s6`, `handlers-global-error-handler.json:s4`, `libraries-failure-log.json:s1`, `libraries-failure-log.json:s3`, `libraries-log.json:s26`, `libraries-log.json:s27`, `handlers-on-error.json:s3`, `web-application-forward-error-page.json:s1`

---