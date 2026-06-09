**結論**: ウェブアプリケーションのエラー処理は、**グローバルエラーハンドラ**と**HTTPエラー制御ハンドラ**の2層でログ出力を行い、エラー画面表示は**HTTPエラー制御ハンドラのデフォルトページ設定**と**OnErrorインターセプタ**で制御する。

---

**根拠**:

### ログ出力の仕組み

ハンドラキューの最上位に位置する**グローバルエラーハンドラ**が、例外・エラーの種別に応じてログを出力する。

| 例外・エラークラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog()` を呼び出しログ出力（レベルは実装クラス依存） |
| `Result.Error`（サブクラス含む） | **FATAL**レベルでログ出力後、`Result.Error`を返却 |
| `ThreadDeath` | **INFO**レベルでログ出力後、リスロー |
| `StackOverflowError`、`OutOfMemoryError` | **FATAL**レベルでログ出力後、`InternalError`を返却 |
| 上記以外の例外・エラー | **FATAL**レベルでログ出力後、`InternalError`を返却 |

ウェブアプリ固有の**HTTPエラー制御ハンドラ**も例外種別に応じてログを出力する。

| 例外クラス | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログ出力なし | `HttpErrorResponse#getResponse()`の値 |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`Result.Error`の場合は `writeFailureLogPattern` プロパティに設定した正規表現が `Error#getStatusCode()` にマッチした場合のみ FATAL レベルのログを出力する。

**フレームワークのログ出力方針**: 1件の障害に対して1件の障害ログを出力する方針。FATAL/ERRORは障害監視の対象、INFOはURLパラメータ改竄エラーや認可チェックエラーなどアプリケーション実行状況に関連するエラーに使用する。

アプリケーションコードから直接障害ログを出力する場合は `FailureLogUtil` を使用する。

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    // 捕捉した例外、処理対象データ、障害コードを指定
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

### エラー画面表示の仕組み

**① HTTPエラー制御ハンドラによるデフォルトページ設定**

ステータスコードに対応したデフォルトのエラーページをコンポーネント設定ファイルで定義する。

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

**② OnErrorインターセプタによるアクションレベルの遷移先指定**

業務アクションのメソッドに `@OnError` アノテーションを付与して、例外クラスと遷移先パスを対応付ける。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**③ カスタムハンドラによる共通エラーページへの遷移**

システム全体で共通のエラーページに遷移させる場合は、ハンドラキューにエラー処理用のカスタムハンドラを追加する。

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

---

**注意点**:
- HTTPエラー制御ハンドラの `defaultPages` 機能を使う場合、`web.xml` の `error-page` 要素との重複設定が必要になる。重複を避けるため、デフォルトエラーページは `web.xml` で設定することを推奨する。
- グローバルエラーハンドラは設定による実装の切り替えができない。ログレベルの細かい調整など要件を満たせない場合は、プロジェクト固有のエラー処理用ハンドラを新たに作成して対応する。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1, libraries-failure-log.json:s3, handlers-on-error.json:s3, libraries-log.json:s27