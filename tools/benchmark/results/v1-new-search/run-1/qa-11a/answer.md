十分な情報が揃いました。Step 5〜8の回答を生成します。

---

**結論**: ウェブアプリケーションでのエラー処理は主に「HTTPエラー制御ハンドラ（`HttpErrorHandler`）」が担当し、例外の種類に応じてログ出力レベルとHTTPレスポンス（エラー画面）を自動的に制御する。エラー画面への遷移先は、`OnError`インターセプタ（アクション単位）またはカスタムハンドラ（システム共通）で定義する。

---

**根拠**:

### 1. ログ出力の仕組み（HTTPエラー制御ハンドラ）

`HttpErrorHandler`（`nablarch.fw.web.handler.HttpErrorHandler`）が後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とレスポンスを生成する：

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | レスポンス内容による |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`HttpErrorResponse`の原因例外が`ApplicationException`（バリデーションエラーなど業務例外）の場合、エラーメッセージを`ErrorMessages`に変換してリクエストスコープ（デフォルトキー: `errors`）に設定する。これによりJSP側でエラーメッセージを表示できる。

`Result.Error`型の例外は`writeFailureLogPattern`に設定した正規表現がステータスコードにマッチした場合のみFATALログを出力する（設定により制御可能）。

### 2. 障害ログの出力方針

障害ログは2種類に分かれる：

- **障害通知ログ**（FATAL/ERROR、ロガー名: `MONITOR`） → 専用ファイルに出力してログ監視ツールで検知
- **障害解析ログ**（FATAL/ERROR、ロガー名: クラス名） → アプリケーションログに出力

```properties
# log.propertiesの例
loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorLog
```

### 3. エラー画面への遷移先の指定方法

3つのパターンがある：

**① `OnError`インターセプタ（アクション単位）**

アクションメソッドに`@OnError`を設定し、例外クラスと遷移先JSPを対応付ける：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

**② カスタムハンドラ（システム共通エラーページ）**

システム全体で共通のエラーページに遷移させたい場合は、カスタムハンドラを作成してハンドラキューに追加する：

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

**③ デフォルトページの設定（`HttpErrorHandler`）**

ステータスコードパターンに対してデフォルトの遷移先を設定できる：

```xml
<component class="nablarch.fw.web.handler.HttpErrorHandler">
  <property name="defaultPages">
    <map>
      <entry key="4.." value="/USER_ERROR.jsp" />
      <entry key="5.." value="/ERROR.jsp" />
    </map>
  </property>
</component>
```

> **注意**: `defaultPages`の設定は`web.xml`の`error-page`設定との重複管理が必要になるため、デフォルトのエラーページ設定は`web.xml`で行うことを推奨する。

---

**注意点**:
- `HttpErrorHandler`は`HTTPレスポンスハンドラ`と`HTTPアクセスログハンドラ`より**後ろ**に配置すること（先に配置すると正常に動作しない）
- `OnError`インターセプタでは1つの例外に対して1つの遷移先しか指定できない。複数の遷移先が必要な場合はアクション内で`try-catch`して`HttpErrorResponse`をスローする

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, web-application-feature-details.json:s16, web-application-forward-error-page.json:s1, web-application-forward-error-page.json:s2, handlers-on-error.json:s3, libraries-failure-log.json:s1

---