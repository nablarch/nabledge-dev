# qa-11 — run-2

## 質問

エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？

## 回答

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

## 参照ナレッジ

- [例外の種類に応じた処理とレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#例外の種類に応じた処理とレスポンスの生成) (s4)
- [nablarch.fw.Result.Errorのログ出力について](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#nablarchfwresulterrorのログ出力について) (s5)
- [デフォルトページの設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#デフォルトページの設定) (s6)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#例外及びエラーに応じた処理内容) (s4)
- [グローバルエラーハンドラでは要件を満たせない場合](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#グローバルエラーハンドラでは要件を満たせない場合) (s5)
- [エラー時の画面遷移とステータスコード](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#エラー時の画面遷移とステータスコード) (s16)
- [ハンドラで共通の振る舞いを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md#ハンドラで共通の振る舞いを定義する) (s1)
- [1つの例外クラスに対して複数の遷移先がある場合の実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-forward-error-page.md#1つの例外クラスに対して複数の遷移先がある場合の実装方法) (s2)
- [OnErrorを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-on-error.md#onerrorを使用する) (s3)
- [障害ログの出力方針](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md#障害ログの出力方針) (s1)
- [障害ログを出力する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-failure-log.md#障害ログを出力する) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output clearly covers both key facts in the expected output. It explicitly describes HttpErrorHandler handling exceptions by type with corresponding HTTP status codes (table showing NoMoreHandlerException→404, HttpErrorResponse→response value, StackOverflowError→500, etc.), and it explicitly states that when HttpErrorResponse's cause is ApplicationException, error messages are converted to ErrorMessages and set in request scope (default key: 'errors') so JSP can display them. Both required facts are present and well-detailed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response perfectly addresses the question about error handling mechanisms, including error screen display and log output - no irrelevant statements were found. Great job! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「HttpErrorHandlerが例外種別に応じたステータスコードのレスポンスを返す」は回答の例外種別テーブル（NoMoreHandlerException→404、StackOverflowError→500等）に含まれている。「ApplicationExceptionのエラーメッセージをリクエストスコープに設定する」は回答の「HttpErrorResponseの原因例外がApplicationExceptionの場合は、エラーメッセージをErrorMessagesに変換してリクエストスコープ（デフォルトキー: errors）に設定する」に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: handlers-HttpErrorHandler.json:s4」等の内部JSON参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | NG | 回答の「上記以外の例外・エラー → FATAL, 500」はナレッジの「java.lang.ThreadDeath と java.lang.VirtualMachineError（StackOverflowError 以外）は本ハンドラでは何もせず上位のハンドラに処理を任せる（エラーを再送出する）」と矛盾する |

### 参照事実（expected_facts）

- HttpErrorHandlerが例外種別に応じたステータスコードのレスポンスを返し、ApplicationExceptionのエラーメッセージをリクエストスコープに設定する
