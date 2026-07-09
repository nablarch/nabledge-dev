**結論**: ウェブアプリケーションでエラーが発生した際のエラー画面表示とログ出力は、主に **HTTPエラー制御ハンドラ**（`HttpErrorHandler`）が担う。このハンドラが例外の種類に応じてログ出力レベルとHTTPステータスコードを決定し、エラー画面（JSPパス）へ遷移させる。

**根拠**:

## 1. HTTPエラー制御ハンドラ（`nablarch.fw.web.handler.HttpErrorHandler`）

ウェブアプリケーションの中心的なエラーハンドラ。後続ハンドラで発生した例外に対してログ出力とHTTPレスポンス生成を行う。

| 例外の種類 | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `nablarch.fw.NoMoreHandlerException` | INFO | 404 | 処理すべきアクションクラスが存在しない |
| `nablarch.fw.web.HttpErrorResponse` | なし | HttpErrorResponseのレスポンス | 業務例外（バリデーションエラー等）。原因が`ApplicationException`の場合はエラーメッセージをリクエストスコープ(`errors`キー)に設定 |
| `nablarch.fw.Result.Error` | 設定による | Error#getStatusCode() | `writeFailureLogPattern`で正規表現設定。マッチした場合FATALログ出力 |
| `java.lang.StackOverflowError` | FATAL | 500 | |
| 上記以外の例外・エラー | FATAL | 500 | |

**エラーページ（デフォルトページ）の設定例**:

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

> **重要**: デフォルトのエラーページ設定は、本機能よりも `web.xml` の `error-page` 要素で設定することを推奨。`web.xml` に設定しない場合、発生箇所によってはウェブサーバのデフォルトエラーページが表示される。

## 2. アクション個別のエラー遷移先（`@OnError`インターセプタ）

業務アクションのメソッドに `@OnError` アノテーションを付けることで、特定例外発生時の遷移先を指定できる。

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

- `type`属性に `RuntimeException` のサブクラスを指定できる
- サブクラスも処理対象になる

## 3. ハンドラで共通エラーページを制御する方法

システム全体で共通のエラーページへ遷移させたい場合は、プロジェクト固有のエラーハンドラを作成する。

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

## 4. 障害ログの出力方針

障害ログは2種類に分けて出力される:

| ログの種類 | ログレベル | ロガー名 |
|---|---|---|
| 障害通知ログ（ログ監視ツール向け） | FATAL、ERROR | MONITOR |
| 障害解析ログ（アプリログ） | FATAL、ERROR | クラス名 |

設定は `log.properties` と `app-log.properties` に記述する。フレームワーク側（`HttpErrorHandler`や`GlobalErrorHandler`）が自動的に障害ログを出力する。

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より**後ろ**に配置すること
- `@OnError` アノテーションは単一例外に対して1つの遷移先しか指定できない。複数パターンが必要な場合は `@OnErrors` を使うか、アクションメソッド内で `try-catch` して `HttpErrorResponse` を返す
- グローバルエラーハンドラ（`GlobalErrorHandler`）はウェブ以外の処理方式（バッチ等）でも使われる汎用ハンドラであり、ウェブアプリでは `HttpErrorHandler` が主役

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