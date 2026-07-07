# qa-12 — run-3

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

**結論**: ウェブアプリケーションでバリデーションエラーメッセージをユーザーに返すには、アクションメソッドに `@InjectForm` と `@OnError` を組み合わせて使用し、テンプレートエンジン側でリクエストスコープの `errors` オブジェクトからエラーメッセージを表示します。

**根拠**:

#### 1. バリデーションの設定

`BeanValidationStrategy` をコンポーネント設定ファイルに定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### 2. Formクラスにバリデーションルールを設定

```java
public class UserForm {
  @Required
  @Length(max = 10)
  private String userName;

  // getter、setterは省略
}
```

メッセージはプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

#### 3. アクションメソッドで `@InjectForm` と `@OnError` を設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  // バリデーション済みのフォームを取得
  UserForm form = ctx.getRequestScopedVar("form");
  // 業務処理...
}
```

`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。

#### 4. エラーメッセージの表示 (Thymeleafの例)

バリデーションエラーが発生すると、`HTTPエラー制御ハンドラ` が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー名 `errors` に格納します。

特定のプロパティに対応したエラーメッセージを表示する場合:

```html
<input type='text' name='form.userName' />
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージをまとめて表示する場合:

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- リクエストスコープのキー名はデフォルトで `errors`。変更したい場合は `WebConfig` の `errorMessageRequestAttributeName` で設定する。
- JSPを使う場合はカスタムタグ（`<n:errors>` 等）でも表示できるが、CSSフレームワークとの相性問題があるため、リクエストスコープのオブジェクトを直接参照する方法も選択できる。

参照: handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s16, libraries-bean-validation.json:s7, web-application-error-message.json

## 参照ナレッジ

- processing-pattern/web-application/web-application-error-message.json:top
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)
- [バリデーションエラー時の遷移先を指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#バリデーションエラー時の遷移先を指定する) (s4)
- [例外の種類に応じた処理とレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-HttpErrorHandler.md#例外の種類に応じた処理とレスポンスの生成) (s4)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.50 | NG | The Expected Output contains a single key fact: displaying error messages using an error display tag that references request scope error messages. The Actual Output does cover this concept — it mentions that error messages are stored in the request scope under the key 'errors' and shows how to retrieve them in templates (both Thymeleaf and JSP with custom tags like <n:errors>). However, the Expected Output specifically emphasizes 'エラー表示タグ' (error display tag) as the primary method, while the Actual Output focuses more on direct template access (Thymeleaf) and only briefly mentions JSP custom tags as an alternative. The core fact about using request scope error messages is covered, but the emphasis on the error display tag as the primary approach is not clearly aligned. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing how to return error messages to users when input validation errors occur. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output incorrectly states that the key name for ErrorMessages in the request scope can be changed in 'WebConfig', when the retrieval context specifies it is configured in the component configuration file using the 'errorMessageRequestAttributeName' property. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- エラー表示タグでリクエストスコープのエラーメッセージを表示する
