**結論**: ウェブアプリケーションのエラー処理は、ハンドラキュー上の「HTTPエラー制御ハンドラ（HttpErrorHandler）」が後続で発生した例外をキャッチし、例外の種類に応じてログ出力とHTTPレスポンス（エラー画面）を生成する仕組みになっている。

---

**根拠**

#### 1. 例外の種類ごとのログとレスポンス（HttpErrorHandler）

| 例外クラス | ログレベル | ステータスコード | 補足 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 証跡ログとして記録 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` | 業務例外はApplicationExceptionのメッセージをリクエストスコープ（キー: `errors`）に設定 |
| `Result.Error` | FATAL（設定による） | `Error#getStatusCode()` | `writeFailureLogPattern` の正規表現がステータスコードにマッチした場合のみFATAL出力 |
| `StackOverflowError` | FATAL | 500 | データや実装バグ起因として障害通知 |
| その他の例外 | FATAL | 500 | 予期しない例外として障害扱い |
| `ThreadDeath` / `VirtualMachineError`（StackOverflowError以外） | — | — | 上位ハンドラに再送出 |

#### 2. エラー画面の設定方法

**方法①：HttpErrorHandlerのデフォルトページ設定**

ステータスコードのパターンにJSPを対応付ける方法。ただし、`web.xml` への設定の方が推奨。

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

**方法②：@OnErrorアノテーション（アクションメソッド個別指定）**

アクションメソッドに対して例外クラスと遷移先を指定する。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**方法③：カスタムハンドラ（システム共通の遷移先）**

個別アクションへのアノテーション設定は漏れや指定ミスのリスクがあるため、システム共通でエラーページを統一する場合はカスタムハンドラを追加する方法が推奨。`HttpErrorResponse` をスローして遷移先とステータスコードを指定する。

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

#### 3. 障害ログの出力方針

障害ログは2種類に分かれる：

| ログの種類 | ログレベル | ロガー名 | 目的 |
|---|---|---|---|
| 障害通知ログ | FATAL、ERROR | `MONITOR` | ログ監視ツールで障害を検知するための専用ファイルに出力 |
| 障害解析ログ | FATAL、ERROR | クラス名 | 障害原因の特定に必要な情報をアプリログに出力 |

フレームワークの方針として、**1件の障害に対して1件の障害ログ**を出力するよう、例外を処理する単一ハンドラで障害通知ログを出力している。INFO レベルはURLパラメータ改竄や認可チェックエラーなど「アプリケーションの実行状況に関連するエラー」に使用する。

---

**注意点**
- `HttpErrorHandler` の `defaultPages` を使う場合、`web.xml` の `<error-page>` 設定も必要。設定しないとウェブサーバのデフォルトエラーページが表示される場合がある。
- `HttpErrorResponse` の原因例外が `ApplicationException` の場合、エラーメッセージはリクエストスコープに `errors` キーで設定される（キー名はコンポーネント設定ファイルで変更可能）。

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-on-error.json:s3, libraries-failure-log.json:s1, libraries-log.json:s27, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1

---