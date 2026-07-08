**結論**: ウェブアプリケーションのエラー処理は、`HttpErrorHandler`（HTTPエラー制御ハンドラ）が中核を担い、例外の種類に応じてログ出力レベルとHTTPステータスコードを自動的に決定する。エラー画面への遷移はデフォルトページ設定・共通ハンドラ・`@OnError`アノテーションの3つの方法で制御する。

---

**根拠**:

#### 1. ログ出力の仕組み（HTTPエラー制御ハンドラ）

後続ハンドラで発生した例外に対し、例外の種類に応じてログ出力とHTTPレスポンスを生成する：

| 例外の種類 | ログレベル | ステータスコード |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | ログなし | HttpErrorResponseのレスポンス |
| `StackOverflowError` | FATAL | 500 |
| 上記以外の例外・エラー | FATAL | 500 |

`Result.Error`の場合は、`writeFailureLogPattern`に設定した正規表現がステータスコードにマッチした場合のみFATALログを出力する。

#### 2. エラー画面遷移の仕組み

3つのレベルで制御できる：

**(a) デフォルトページ（全体）**: `HttpErrorHandler`の`defaultPages`でステータスコードに対応するページを設定：

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

**(b) 共通ハンドラ（システム全体）**: 独自ハンドラで特定例外をキャッチし`HttpErrorResponse`をスロー：

```java
public class ExampleErrorForwardHandler implements Handler<Object, Object> {
  @Override
  public Object handle(Object data, ExecutionContext context){
    try {
      return context.handleNext(data);
    } catch (NoDataException e) {
      throw new HttpErrorResponse(
          404, "/WEB-INF/view/common/errorPages/pageNotFoundError.jsp", e);
    }
  }
}
```

**(c) アクションレベル（個別）**: `@OnError`アノテーションで例外クラスと遷移先を指定：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

#### 3. バリデーションエラーのメッセージ表示

`HttpErrorResponse`の原因が`ApplicationException`の場合、エラーメッセージが自動的に`ErrorMessages`に変換され、リクエストスコープのキー`errors`に設定される。JSP側ではこのキーでエラーメッセージを参照できる（キー名はコンポーネント設定で変更可）。

#### 4. 障害ログ出力の方針

障害ログは2種類に分かれる：
- **障害通知ログ**: FATAL/ERROR、ロガー名`MONITOR` → 専用の監視ファイルに出力
- **障害解析ログ**: FATAL/ERROR、クラス名のロガー → アプリケーションログに出力

アプリケーションから障害ログを出力する場合は`FailureLogUtil`を使用：

```java
FailureLogUtil.logError(e, inputData, "FAILURE_CODE");
```

---

**注意点**:
- `HttpErrorHandler`は`HttpResponseHandler`より後ろ、かつ`HttpAccessLogHandler`より後ろに配置する必要がある
- `defaultPages`でデフォルトページを設定する場合、`web.xml`のerror-page要素への重複設定も必要。`web.xml`への設定を推奨する

---

参照:
- HTTPエラー制御ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md
  例外の種類に応じた処理とレスポンスの生成
  nablarch.fw.Result.Errorのログ出力について
  デフォルトページの設定
- OnErrorインターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md
  OnErrorを使用する
- エラー時の遷移先の指定方法
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md
  ハンドラで共通の振る舞いを定義する
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
  エラー時の画面遷移とステータスコード
- 障害ログの出力
  .claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md
  障害ログの出力方針
  障害ログを出力する