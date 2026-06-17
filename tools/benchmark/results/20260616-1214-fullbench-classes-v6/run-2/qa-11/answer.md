**結論**: ウェブアプリケーションでは、**HTTPエラー制御ハンドラ**（`HttpErrorHandler`）がエラー画面への遷移とHTTPレスポンス生成を担当し、**グローバルエラーハンドラ**（`GlobalErrorHandler`）が未捕捉例外のログ出力を担当する二層構造になっています。

---

**根拠**:

#### 1. HTTPエラー制御ハンドラ（HttpErrorHandler）

後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とHTTPレスポンスを生成します。

| 例外クラス | ログ | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし（業務例外扱い） | レスポンスに設定された値 |
| `Result.Error` | `writeFailureLogPattern` の設定次第 | エラーのステータスコード |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージを `ErrorMessages` に変換してリクエストスコープ（デフォルトキー: `errors`）に設定するため、JSPでエラーメッセージを表示できます。

**デフォルトエラーページの設定**（ステータスコード別）:
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
> 推奨: デフォルトエラーページは `web.xml` の `error-page` 要素で設定する方が確実。

---

#### 2. グローバルエラーハンドラ（GlobalErrorHandler）

未捕捉例外をハンドラキューの先頭で捕捉し、ログを出力します（ウェブ以外の処理方式でも共通）。

| 例外クラス | ログ |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` で出力（レベルは実装クラス次第） |
| `Result.Error`（サブクラス含む） | FATALレベル |
| 上記以外 | FATALレベル |

---

#### 3. アクション個別のエラー画面遷移

`@OnError` アノテーションでアクションメソッドごとに遷移先を指定できます：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

システム全体で共通の遷移先を設定したい場合は、エラー用ハンドラを作成して `HttpErrorResponse` をスローする方法が推奨されます：

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context) {
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    }
  }
}
```

---

#### 4. 障害ログの出力方針

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（監視ツール用） | FATAL、ERROR | MONITOR |
| 障害解析ログ | FATAL、ERROR | クラス名 |

設定は `log.properties` と `app-log.properties` で行います。

---

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より後ろに配置する必要があります。
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置します。
- `GlobalErrorHandler` の動作は設定で切り替えられないため、要件に合わない場合はプロジェクト固有のエラーハンドラを作成します。

参照:
- `handlers-HttpErrorHandler.json:s4`
- `handlers-HttpErrorHandler.json:s5`
- `handlers-HttpErrorHandler.json:s6`
- `handlers-global-error-handler.json:s4`
- `web-application-feature-details.json:s16`
- `web-application-forward-error-page.json:s1`
- `handlers-on-error.json:s3`
- `libraries-failure-log.json:s1`