# qa-12 — run-1

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

ウェブアプリケーションでバリデーションエラー時にエラーメッセージを返す手順は以下のとおりです。

---

#### 1. 業務アクションに `@InjectForm` と `@OnError` を設定する

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

- `@InjectForm` がリクエストパラメータのバリデーションを実行し、エラー時は `ApplicationException` をスローします。
- `@OnError` でエラー時の遷移先を指定します。**`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いになる**ため必須です。
- `path` に `"forward://メソッド名"` を指定することで、初期表示データを取得するメソッドに内部フォワードしてから画面を表示できます。

#### 2. フレームワークがエラーメッセージをリクエストスコープに設定する

`HttpErrorHandler` が `ApplicationException` を `ErrorMessages` オブジェクトに変換し、リクエストスコープに **`errors`** というキーで格納します。この処理はフレームワーク側で自動的に行われます。

#### 3. 画面にエラーメッセージを表示する

**Thymeleaf の場合**

```html
<!-- 特定項目のエラー -->
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- グローバルメッセージ（相関バリデーション等） -->
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>

<!-- 全エラーメッセージ -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**JSP の場合**

```jsp
<!-- 特定項目のエラー（個別表示） -->
<n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />

<!-- 全エラーメッセージ一覧（まとめて表示） -->
<n:errors filter="all" errorCss="alert alert-danger" />

<!-- グローバルメッセージのみ -->
<n:errors filter="global" errorCss="alert alert-danger" />
```

JSP カスタムタグは、エラーがあった入力項目の CSS クラスに `nablarch_error` を自動的に追加するため、入力項目のハイライト表示も可能です。

```css
input.nablarch_error, select.nablarch_error {
  background-color: #FFFFB3;
}
```

#### 注意点

- `ErrorMessages` のリクエストスコープキーはデフォルト `errors` です。変更が必要な場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定します。
- バリデーションに Bean Validation を使用する場合は、`BeanValidationStrategy` を `validationStrategy` コンポーネントとして登録する必要があります。
- エラー時の遷移先画面でプルダウンの選択肢等の表示データが必要な場合は、`@OnError` の `path` に `"forward://初期表示メソッド"` を指定して初期表示用メソッドに内部フォワードします。

---

参照:
- [バリデーションエラーのメッセージを画面表示する](processing-pattern/web-application/web-application-error-message.json)
- [InjectForm インターセプタ](component/handlers/handlers-InjectForm.json)
- [OnError インターセプタ](component/handlers/handlers-on-error.json)
- [Bean Validation](component/libraries/libraries-bean-validation.json)
- [カスタムタグ](component/libraries/libraries-tag.json)

## 参照ナレッジ

（なし）

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.60 | NG | The Expected Output contains a single specific fact: 'エラー表示タグでリクエストスコープのエラーメッセージを表示する' (Display error messages from request scope using error display tags). The Actual Output does cover the concept of displaying error messages from the request scope using display tags (e.g., JSP custom tags like `<n:error>` and `<n:errors>`, and Thymeleaf templates accessing `${errors}`), and it mentions that `HttpErrorHandler` stores error messages in the request scope under the key `errors`. However, the Actual Output is a comprehensive guide covering multiple topics far beyond the single expected fact, and while the core concept is present, it is embedded within extensive additional content. The key fact about using error display tags to show request-scoped error messages is addressed, but not as a concise, focused statement matching the Expected Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input question about how to return error messages to users when input validation errors occur. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- エラー表示タグでリクエストスコープのエラーメッセージを表示する
