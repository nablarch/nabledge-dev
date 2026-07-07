# qa-03 — run-1

## 質問

2つの入力項目が一致しているかチェックしたい。メールアドレスと確認用メールアドレスの相関バリデーションのやり方を教えてほしい

## 回答

**結論**: `@AssertTrue` アノテーションを使用したメソッドをFormクラスに定義し、`Objects.equals()` で2項目を比較する。ウェブアプリケーションでは `@InjectForm` インターセプタ経由でバリデーションが実行される。

**根拠**:

相関バリデーションは、FormクラスにbooleanメソッドとJakarta Bean Validationの `@AssertTrue` アノテーションを組み合わせて実装する。

```java
public class SampleForm {
  private String mailAddress;

  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    return Objects.equals(mailAddress, confirmMailAddress);
  }
}
```

メールアドレスが任意項目（未入力を許容する）の場合は、どちらかが未入力のときに相関バリデーションをスキップする必要がある。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は、相関バリデーションは実施しない。(バリデーションOKとする)
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

ウェブアプリケーションでバリデーションを実行するには、業務アクションのメソッドに `@InjectForm` を設定する。

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う
}
```

Bean Validationを `@InjectForm` で使用するには、コンポーネント設定ファイルに以下の設定が必要。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されない。項目単体のバリデーション（`@Required`など）より前に相関バリデーションが実行される場合があるため、相関バリデーションメソッド内で予期せぬ例外が発生しないよう実装すること。
- `@OnError` を `@InjectForm` と合わせて設定しないと、バリデーションエラーがシステムエラー扱いになる。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3

## 参照ナレッジ

- [相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#相関バリデーションを行う) (s11)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)
- [InjectFormを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md#injectformを使用する) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the key fact from the Expected Output: using Jakarta Bean Validation's @AssertTrue annotation to perform correlation validation. It not only confirms this core fact but provides detailed implementation examples, edge cases, and configuration details. The expected fact is fully present and not contradicted. |
| answer_relevancy | 0.95 | 0.94 | NG | The score is 0.94 because the response is highly relevant to the question about implementing correlation validation for email address and confirmation email fields. It is only slightly penalized due to a reference to source documents that does not add any substantive value to the actual implementation guidance. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う」は回答の「`@AssertTrue` アノテーションを使用したメソッドをFormクラスに定義し」および本文のコード例に明確に含まれている |
| answer_relevancy | OK | 回答の全内容（@AssertTrueの使い方、任意項目の場合の処理、@InjectFormの設定、BeanValidationStrategyの設定、実行順序の注意点、@OnErrorの注意点）は質問「メールアドレスと確認用メールアドレスの相関バリデーション」に直接答えている。末尾の「参照:」行は参照元の引用であり実質的な情報ではないが、回答本体に的外れな情報は含まれていない。DeepEvalがスコア0.94でNGとした理由（参照リストが価値を付加しない）は厳密すぎる判定であり、人手判定ではOKが妥当。 |
| faithfulness | OK | 回答の内容はナレッジMD（libraries-bean-validation.md）の「相関バリデーションを行う」セクションおよび「ウェブアプリケーションのユーザ入力値のチェックを行う」セクションと完全に一致している。@AssertTrueのコード例、任意項目時のStringUtil.isNullOrEmptyを使ったスキップ処理、BeanValidationStrategyのXML設定、実行順序が保証されないという注意点はすべてナレッジの記述を正確に反映しており、矛盾は見当たらない。 |

### 参照事実（expected_facts）

- Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う
