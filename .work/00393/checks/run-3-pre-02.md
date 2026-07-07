# pre-02 — run-3

## 質問

入力チェック（バリデーション）の実装方法を教えてください

## 回答

**結論**: ウェブアプリケーションのバリデーションは `@InjectForm` インターセプタを業務アクションメソッドに設定することで実装する。Formクラスにバリデーションアノテーションを定義し、`@OnError` でエラー時の遷移先を指定する。

---

**根拠**:

**1. コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスを作成する（プロパティは全て `String` 型）**

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterは省略
}
```

ドメインバリデーションを使うと、バリデーションルールの変更が容易になるため推奨:

```java
// ドメインBeanにルールを集中定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// 各FormではDomainアノテーションで参照する
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;

  // getter、setterは省略
}
```

**3. 業務アクションに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

---

**注意点**:
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること
- Formのプロパティは必ず `String` 型にすること。`String` 以外の型があると、不正な値が送信された際に変換処理が失敗して障害になる
- データベースとの相関バリデーション（重複チェックなど）は、SQL インジェクション等を防ぐため業務アクション側で実装すること

参照: component/libraries/libraries-bean-validation.json:s6, s7, s8, s9, s16 / component/handlers/handlers-InjectForm.json:s3, s4

## 参照ナレッジ

- [Bean Validationを使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#bean-validationを使うための設定) (s6)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)
- [ドメインバリデーションを使う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ドメインバリデーションを使う) (s9)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)
- [バリデーションエラー時の遷移先を指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#バリデーションエラー時の遷移先を指定する) (s4)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [入力値のチェック](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#入力値のチェック) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The expected output contains one key fact: WebアプリケーションではInjectFormインターセプタを使用してバリデーションを行う (In web applications, validation is performed using the InjectForm interceptor). The actual output explicitly covers this fact in both the conclusion section ('ウェブアプリケーションのバリデーションは @InjectForm インターセプタを業務アクションメソッドに設定することで実装する') and in the code examples showing @InjectForm usage. All expected facts are covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response perfectly addresses the question about implementing input validation (バリデーション) with no irrelevant statements. Great job staying fully on topic! |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output states that all properties in the Bean class must be defined as String, presenting it as a strict requirement, whereas the retrieval context only recommends this practice without making it mandatory. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- WebアプリケーションではInjectFormインターセプタを使用してバリデーションを行う
