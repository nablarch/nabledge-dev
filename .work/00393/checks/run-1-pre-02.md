# pre-02 — run-1

## 質問

入力チェック（バリデーション）の実装方法を教えてください

## 回答

**結論**: ウェブアプリケーションの入力チェックは `@InjectForm` インターセプタとBean Validationを組み合わせて実装する。Formクラスにバリデーションアノテーションを設定し、業務アクションメソッドに `@InjectForm` を付与することでバリデーションが自動実行される。

**根拠**:

**1. コンポーネント設定ファイルの準備**

`BeanValidationStrategy` を `validationStrategy` という名前で登録する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスの実装**

プロパティは**必ずString型**で定義し、バリデーションアノテーションを付与する。ドメインバリデーションの使用を推奨。

```java
public class ClientForm implements Serializable {

    @Required
    @Domain("clientName")   // ドメインバリデーション使用推奨
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;

    // getter、setter省略
}
```

ドメインBeanとDomainManagerの定義:

```java
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String clientName;

    @Length(max = 2)
    @SystemChar(charsetDef = "半角数字")
    String industryCode;
}
```

```xml
<!-- domainManagerという名前で登録 -->
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**3. 業務アクションへの`@InjectForm`設定**

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {

    // バリデーション済みフォームをリクエストスコープから取得
    ClientForm form = context.getRequestScopedVar("form");

    // 以降、業務処理を行う
}
```

ポイント:
- `prefix = "form"` は `form.xxx` という名前のリクエストパラメータをバリデーション対象とする
- `@OnError` を必ず設定すること。未設定の場合バリデーションエラーがシステムエラー扱いになる
- バリデーション済みフォームは `ctx.getRequestScopedVar("form")` で取得できる

**注意点**:
- Formのプロパティは全てString型にすること。String以外の型だと変換失敗時に予期せぬ例外が発生する
- `@Required` アノテーションはドメインBeanに設定せず、各Formクラス側に設定すること（必須かどうかは機能設計による）
- データベースとの相関バリデーション（重複チェック等）はBean Validationではなく業務アクション側で実装すること（バリデーション前の安全でない値でDBアクセスするとSQLインジェクションリスクがある）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, libraries-bean-validation.json:s9, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4

## 参照ナレッジ

- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [ドメインバリデーションを使う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ドメインバリデーションを使う) (s9)
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)
- [Bean Validationを使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#bean-validationを使うための設定) (s6)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [バリデーションエラー時の遷移先を指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#バリデーションエラー時の遷移先を指定する) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the single key fact in the Expected Output: that web applications use the InjectForm interceptor to perform validation. The Actual Output explicitly mentions '@InjectForm インターセプタ' and provides detailed implementation steps, which directly addresses and expands upon the expected fact. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing how to implement input validation (バリデーション) with no irrelevant statements. Great job staying focused and on-topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- WebアプリケーションではInjectFormインターセプタを使用してバリデーションを行う
