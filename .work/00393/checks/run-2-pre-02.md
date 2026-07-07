# pre-02 — run-2

## 質問

入力チェック（バリデーション）の実装方法を教えてください

## 回答

**結論**: ウェブアプリケーションでの入力チェックは、`@InjectForm` インターセプタを業務アクションのメソッドに付与し、Formクラスに Bean Validation アノテーションを設定することで実装します。

**根拠**:

**Step 1: コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Step 2: Formクラスにバリデーションルールを設定する**

Formクラスのプロパティは **必ず `String` 型で宣言**すること。アノテーションはフィールドまたはgetterに設定する（setterには無効）。

ドメインバリデーション（推奨）を使う場合は、ドメインBeanを先に定義する:

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManagerの作成とコンポーネント設定
// <component name="domainManager" class="sample.SampleDomainManager"/>
```

FormクラスでDomainアノテーションを使う:

```java
public class ClientForm implements Serializable {

    @Required
    @Domain("name")
    private String clientName;

    @Domain("date")
    private String birthday;

    // getter、setter省略
}
```

**Step 3: 業務アクションに `@InjectForm` と `@OnError` を付与する**

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {

    // バリデーション済みオブジェクトをリクエストスコープから取得
    ClientForm form = context.getRequestScopedVar("form");

    // 業務処理を実行
}
```

- `prefix = "form"` は `form.clientName` のようにHTMLのname属性のプレフィックスと一致させる
- バリデーション成功時、バリデーション済みフォームがリクエストスコープ（デフォルトキー名: `"form"`）に格納される

**Step 4: エラーメッセージをプロパティファイルに定義する**

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、必ず付与すること
- Formプロパティを `String` 以外の型にすると、不正な入力値でBeanへの変換が失敗し障害につながる
- データベースとの相関バリデーションは、SQLインジェクション防止のため業務アクション側で実装すること（Bean Validationの中でDBアクセスを行わない）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, libraries-bean-validation.json:s9, libraries-bean-validation.json:s7, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4

## 参照ナレッジ

- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [ドメインバリデーションを使う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ドメインバリデーションを使う) (s9)
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)
- [バリデーションエラー時の遷移先を指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#バリデーションエラー時の遷移先を指定する) (s4)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [Bean Validationを使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#bean-validationを使うための設定) (s6)
- [入力値のチェック](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#入力値のチェック) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers the key fact from the Expected Output: it states that `@InjectForm` interceptor is used for validation in web applications (mentioned in the conclusion and Step 3). The expected fact about using InjectForm interceptor for validation in web applications is clearly and thoroughly covered. |
| answer_relevancy | 0.95 | 0.95 | OK | The score is 0.95 because the response is highly relevant to the question about input validation implementation. However, it loses some points for including an inaccurate statement about SQL injection prevention being a reason why Bean Validation does not perform DB access, when the actual reasons are related to transaction management and separation of responsibilities. This minor inaccuracy slightly detracts from an otherwise well-targeted response. |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output incorrectly states that defining all Bean class properties as String is mandatory ('しなければならない'), when the retrieval context only states that it is 'recommended' (推奨). |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「WebアプリケーションではInjectFormインターセプタを使用してバリデーションを行う」は回答の結論「`@InjectForm` インターセプタを業務アクションのメソッドに付与し」およびStep 3のコード例に明確に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, ...」などの内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ（バリデーションルールの設定方法 Tipブロック）は「プロパティは必ず String とすること」と明記しており、回答の「必ず `String` 型で宣言すること」と矛盾しない。DeepEvalが「推奨にすぎない」と判断したのは誤り |

### 参照事実（expected_facts）

- WebアプリケーションではInjectFormインターセプタを使用してバリデーションを行う
