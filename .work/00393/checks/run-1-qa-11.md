# qa-11 — run-1

## 質問

エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？

## 回答

**結論**: ウェブアプリケーションのエラー処理は、**HTTPエラー制御ハンドラ（HttpErrorHandler）** が例外の種類に応じたログ出力とHTTPレスポンス（エラー画面）生成を一元的に担う。個別のアクションへの遷移先制御には `@OnError` インターセプタ、未捕捉例外の処理には **グローバルエラーハンドラ**、障害ログ出力には専用の障害ログ機能が使われる多層構造になっている。

---

**根拠**:

### 1. HTTPエラー制御ハンドラ（HttpErrorHandler）

後続ハンドラで発生した例外を捕捉し、例外の種類に応じてログ出力とHTTPレスポンスを生成する。

| 例外クラス | ログレベル | HTTPステータス |
|---|---|---|
| `NoMoreHandlerException` | INFO | 404 |
| `HttpErrorResponse` | なし | `HttpErrorResponse#getResponse()` |
| `Result.Error` | `writeFailureLogPattern` に一致すれば FATAL | `Error#getStatusCode()` |
| `StackOverflowError` | FATAL | 500 |
| 上記以外すべて | FATAL | 500 |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージを `ErrorMessages` に変換してリクエストスコープの `errors` キーに自動設定する（JSPで `<n:errors>` タグを使って表示可能）。

ステータスコードに対応するデフォルトのエラーページはコンポーネント設定で指定する：

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

### 2. グローバルエラーハンドラ（GlobalErrorHandler）

ハンドラキューの先頭近くに配置し、未捕捉の例外・エラーを捕捉してログ出力と結果返却を行う。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出しログ出力後、`ServiceError` を返却 |
| `Result.Error`（サブクラス含む） | FATAL レベルのログ出力後、`Result.Error` を返却 |
| 上記以外 | FATAL レベルのログ出力後、`InternalError` を生成して返却 |

### 3. アクション単位のエラー画面遷移（OnError インターセプタ）

業務アクションのメソッドに `@OnError` アノテーションを設定し、例外発生時の遷移先を指定する：

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

エラー時の遷移先画面でデータ表示が必要な場合は、内部フォワードを使う：

```java
@InjectForm(form = PersonForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://initializeRegisterPage")
public HttpResponse confirmForRegister(HttpRequest request, ExecutionContext context) {
    PersonForm form = context.getRequestScopedVar("form");
    return new HttpResponse("/WEB-INF/view/person/confirmForRegister.jsp");
}

public HttpResponse initializeRegisterPage(HttpRequest request, ExecutionContext context) {
    // 画面表示データをデータベースなどから取得し、リクエストスコープに設定する
    return new HttpResponse("/WEB-INF/view/person/inputForRegister.jsp");
}
```

### 4. システム共通のエラーページ制御（カスタムハンドラ）

複数アクションに同じ遷移先を設定するよりも、カスタムハンドラをハンドラキューに追加する方が確実：

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

### 5. 障害ログの出力

障害ログは2種類に分けて出力される：

| ログの種類 | ログレベル | ロガー名 | 用途 |
|---|---|---|---|
| 障害通知ログ | FATAL / ERROR | MONITOR | ログ監視ツールによる障害検知専用ファイル |
| 障害解析ログ | FATAL / ERROR | クラス名 | アプリケーションログ全体 |

フレームワークの例外ハンドラが自動出力する。アプリケーション側で出力する場合は `FailureLogUtil` を使う：

```java
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

---

**注意点**:
- `HttpErrorHandler` は `HttpResponseHandler`（HTTPレスポンスハンドラ）より後ろに配置すること（生成した `HttpResponse` を `HttpResponseHandler` が処理するため）
- `GlobalErrorHandler` はできるだけハンドラキューの先頭に配置すること
- `HttpErrorHandler` の `defaultPages` を使う場合、`web.xml` の `error-page` 要素も設定することを推奨（設定がないとウェブサーバのデフォルトエラーページが表示される場合がある）

参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, handlers-HttpErrorHandler.json:s6, handlers-global-error-handler.json:s4, handlers-on-error.json:s3, handlers-on-error.json:s4, web-application-forward-error-page.json:s1, libraries-failure-log.json:s1, libraries-failure-log.json:s3

## 参照ナレッジ

- [例外の種類に応じた処理とレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#例外の種類に応じた処理とレスポンスの生成) (s4)
- [nablarch.fw.Result.Errorのログ出力について](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#nablarchfwresulterrorのログ出力について) (s5)
- [デフォルトページの設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#デフォルトページの設定) (s6)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#制約) (s3)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#例外及びエラーに応じた処理内容) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#制約) (s3)
- [OnErrorを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md#onerrorを使用する) (s3)
- [エラー時の遷移先画面に表示するデータを取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md#エラー時の遷移先画面に表示するデータを取得する) (s4)
- [複数のレスポンスを指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md#複数のレスポンスを指定する) (s5)
- [ハンドラで共通の振る舞いを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md#ハンドラで共通の振る舞いを定義する) (s1)
- [1つの例外クラスに対して複数の遷移先がある場合の実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md#1つの例外クラスに対して複数の遷移先がある場合の実装方法) (s2)
- [エラー時の画面遷移とステータスコード](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#エラー時の画面遷移とステータスコード) (s16)
- [障害ログの出力方針](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md#障害ログの出力方針) (s1)
- [障害ログを出力する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md#障害ログを出力する) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output thoroughly covers the expected facts. It explicitly describes HttpErrorHandler handling exceptions based on type with corresponding HTTP status codes (via the table showing NoMoreHandlerException→404, HttpErrorResponse→its own status, etc., and 500 for others). It also explicitly states that when HttpErrorResponse's cause is ApplicationException, error messages are converted to ErrorMessages and set in the request scope under the 'errors' key, which directly corresponds to the expected fact about ApplicationException error messages being set in the request scope. Both key facts from the Expected Output are present and well-explained. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about error handling mechanisms, including error screen display and log output. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.96 | NG | The score is 0.96 because the actual output contains a minor misrepresentation regarding FATAL level logging for Result.Error. The retrieval context states that FATAL level logging is performed for Result.Error (including subclasses) unconditionally, while the actual output implies that FATAL logging is conditional on the writeFailureLogPattern matching Error#getStatusCode(), which is not supported by the retrieval context. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「HttpErrorHandlerが例外種別に応じたステータスコードのレスポンスを返す」は回答のセクション1の例外クラス×HTTPステータスコード対応表に含まれている。参照事実「ApplicationExceptionのエラーメッセージをリクエストスコープに設定する」は回答の「HttpErrorResponse の原因例外が ApplicationException の場合は、エラーメッセージを ErrorMessages に変換してリクエストスコープの errors キーに自動設定する」に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: handlers-HttpErrorHandler.json:s4, handlers-HttpErrorHandler.json:s5, ...」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし。回答の「writeFailureLogPattern に一致すれば FATAL」は、ナレッジ（handlers-HttpErrorHandler.md「nablarch.fw.Result.Errorのログ出力について」）の「その正規表現が Error#getStatusCode() とマッチした場合に FATAL レベルのログを出力する」と一致しており、DeepEvalのNG判定は誤り（false positive） |

### 参照事実（expected_facts）

- HttpErrorHandlerが例外種別に応じたステータスコードのレスポンスを返し、ApplicationExceptionのエラーメッセージをリクエストスコープに設定する
