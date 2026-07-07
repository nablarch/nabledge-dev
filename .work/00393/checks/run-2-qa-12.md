# qa-12 — run-2

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

**結論**: ウェブアプリケーションで入力チェックエラーをユーザーに返すには、①`@InjectForm` + `@OnError` でバリデーション実行とエラー画面遷移を設定し、②テンプレート（ThymeleafまたはJSP）でリクエストスコープの `ErrorMessages`（キー名: `errors`）にアクセスしてエラーメッセージを表示する。

**根拠**:

**Step 1: アクション側でバリデーションとエラー遷移先を設定**

`@InjectForm` アノテーションで入力値のバリデーションを実行し、`@OnError` でエラー時の遷移先を指定する。`@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必須。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

**Step 2: エラーメッセージの仕組み**

バリデーションエラー発生時、`HTTPエラー制御ハンドラ`が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープにキー名 `errors`（デフォルト）で設定する。

**Step 3: テンプレートでエラーメッセージを表示**

Thymeleafの場合:
```html
<!-- 特定プロパティのエラーメッセージを表示 -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- すべてのエラーメッセージを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>

<!-- グローバルメッセージ（プロパティに紐付かない）を表示 -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

JSP（Nablarchカスタムタグ）の場合:
```jsp
<!-- すべてのエラーメッセージを一覧表示 -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- 特定項目のエラーメッセージを個別表示 -->
<n:text name="form.userName" />
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
```

**エラーメッセージの定義**: `@InjectForm` で Bean Validation を使う場合、メッセージはプロパティファイルで定義する（デフォルトで `NablarchMessageInterpolator` がメッセージ管理を使用）。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**Bean Validation のコンポーネント設定**（`@InjectForm` で Bean Validation を使う場合に必要）:
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- `@OnError` が設定されていないとバリデーションエラーがシステムエラー扱いになる
- リクエストスコープのキー名はデフォルト `errors`。変更する場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定
- JSPカスタムタグはDOM構造の制約によりCSSフレームワークと相性が悪いことがある。Thymeleafなどでリクエストスコープに直接アクセスする方法が推奨

参照: component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-HttpErrorHandler.json:s4, component/libraries/libraries-bean-validation.json:s7, component/libraries/libraries-bean-validation.json:s16, component/libraries/libraries-tag.json:s29

## 参照ナレッジ

- processing-pattern/web-application/web-application-error-message.json:全体
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)
- [バリデーションエラー時の遷移先を指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#バリデーションエラー時の遷移先を指定する) (s4)
- [例外の種類に応じた処理とレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#例外の種類に応じた処理とレスポンスの生成) (s4)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [特定の項目に紐づくバリデーションエラーのメッセージを作りたい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#特定の項目に紐づくバリデーションエラーのメッセージを作りたい) (s13)
- [エラー表示を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md#エラー表示を行う) (s29)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Expected Output contains a single key fact: displaying error messages from the request scope using error display tags. The Actual Output explicitly covers this fact, demonstrating both JSP custom tags (n:errors, n:error) and Thymeleaf templates accessing request-scoped ErrorMessages (key: 'errors') to display validation error messages. The Actual Output fully satisfies the expected fact and provides extensive additional detail. |
| answer_relevancy | 0.95 | 0.86 | NG | The score is 0.86 because the response mostly addresses how to return error messages to users during input validation, but loses some points due to irrelevant content: a duplicate statement, and two subjective recommendations comparing JSP vs Thymeleaf/CSS framework compatibility, which go beyond the scope of the question asked. |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output is largely faithful to the retrieval context, with only a minor inaccuracy where it states the key name can be changed in a 'WebConfig' class, whereas the retrieval context specifies it is configured via the 'errorMessageRequestAttributeName' property in the component configuration file. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「エラー表示タグでリクエストスコープのエラーメッセージを表示する」は回答の「Step 3: テンプレートでエラーメッセージを表示」でJSPカスタムタグ（n:errors, n:error）およびThymeleafでリクエストスコープの`${errors}`にアクセスする方法として含まれている |
| answer_relevancy | NG | 回答末尾の「参照: component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, ...」など内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | 回答の「WebConfig の errorMessageRequestAttributeName プロパティで設定」はナレッジ（handlers-HttpErrorHandler.md）の「コンポーネント設定ファイルで変更できる」およびXML例（`<component name="webConfig" class="nablarch.common.web.WebConfig">` の `errorMessageRequestAttributeName` プロパティ）と矛盾しない |

### 参照事実（expected_facts）

- エラー表示タグでリクエストスコープのエラーメッセージを表示する
