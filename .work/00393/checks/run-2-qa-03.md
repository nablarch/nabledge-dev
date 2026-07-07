# qa-03 — run-2

## 質問

2つの入力項目が一致しているかチェックしたい。メールアドレスと確認用メールアドレスの相関バリデーションのやり方を教えてほしい

## 回答

**結論**: Bean Validationを使う場合は `@AssertTrue` アノテーションを付与したgetterメソッドで相関バリデーションを実装する。Nablarch Validationを使う場合は `@ValidateFor` アノテーション付きのstaticメソッドで実装する。

---

**根拠**:

**Bean Validation（推奨）の実装例**

```java
public class SampleForm {
  private String mailAddress;
  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      // どちらかが未入力の場合は相関バリデーションを実施しない
      return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }
}
```

ウェブアプリケーションでBean Validationを使うには、コンポーネント設定ファイルに以下を追加する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

---

**Nablarch Validation の実装例**

```java
public class SampleForm {

  @Domain(SampleDomain.MAIL)
  @Required
  public void setMailAddress(String mailAddress) {
      this.mailAddress = mailAddress;
  }

  @Domain(SampleDomain.MAIL)
  @Required
  public void setConfirmMailAddress(String confirmMailAddress) {
      this.confirmMailAddress = confirmMailAddress;
  }

  @ValidateFor("validate")
  public static void validate(ValidationContext<SampleForm> context) {
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      if (!context.isValid()) {
          return;
      }

      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

---

**注意点**:
- Bean Validationでは実行順序が保証されないため、任意項目の場合は未入力時に `true` を返す処理を入れること（項目単体のバリデーションが実行されていない状態で相関バリデーションが呼び出されることがある）
- Nablarch Validationでは、項目ごとのバリデーションでエラーが発生した場合は `context.isValid()` でチェックして相関バリデーションをスキップすること

参照: component/libraries/libraries-bean-validation.json:s11, component/libraries/libraries-nablarch-validation.json:s14, component/libraries/libraries-bean-validation.json:s16

## 参照ナレッジ

- [相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#相関バリデーションを行う) (s11)
- [相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-nablarch-validation.md#相関バリデーションを行う) (s14)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers the key fact in the Expected Output: using @AssertTrue annotation for correlation validation with Bean Validation. The Actual Output provides a detailed implementation example showing @AssertTrue on a getter method, which directly corresponds to the expected fact about using Jakarta Bean Validation's @AssertTrue for cross-field validation. The coverage is complete for the single expected fact. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about cross-field validation for email and confirmation email fields with no irrelevant statements. Great job! |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output incorrectly states that the @ValidateFor annotation must be set on a static method, whereas the retrieval context only specifies that it is set on a method in a Bean class, with no requirement that the method be static. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う」は回答の `@AssertTrue(message = "{compareMailAddress}")` を付与したgetterメソッドの実装例に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う
