# qa-03 — run-3

## 質問

2つの入力項目が一致しているかチェックしたい。メールアドレスと確認用メールアドレスの相関バリデーションのやり方を教えてほしい

## 回答

**結論**: フォームクラスに `@AssertTrue` アノテーションを付けた `boolean` 型メソッドを追加して実装する。

**根拠**:

```java
public class SampleForm {
  private String mailAddress;

  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    return Objects.equals(mailAddress, confirmMailAddress);
  }

  // getter、setterは省略
}
```

メソッドが `false` を返した場合、`message` 属性に指定したメッセージID `{compareMailAddress}` のメッセージがエラーとして通知される。

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションより前に相関バリデーションが呼び出される場合がある。
- `mailAddress` や `confirmMailAddress` が任意項目の場合、どちらかが未入力のときに `NullPointerException` などの予期せぬ例外が発生しないよう、以下のように未入力チェックを追加すること。

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

参照: libraries-bean-validation.json:s11

## 参照ナレッジ

- [相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#相関バリデーションを行う) (s11)
- [ウェブアプリケーションのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#ウェブアプリケーションのユーザ入力値のチェックを行う) (s16)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers the key fact from the Expected Output: using Jakarta Bean Validation's @AssertTrue annotation to perform correlation validation. The Actual Output not only confirms this approach but provides detailed code examples and additional notes about implementation, fully addressing the expected fact. |
| answer_relevancy | 0.95 | 0.92 | NG | The score is 0.92 because the response was largely relevant and addressed the correlation validation for email and confirmation email fields. However, it was slightly penalized for including a reference to a source file that did not contribute any meaningful information to answering the question. |
| faithfulness | 0.99 | 0.88 | NG | The score is 0.88 because the actual output incorrectly states that a NullPointerException will occur when item-level validation has not been executed, whereas the retrieval context actually instructs that the logic must be implemented to *prevent* unexpected exceptions from occurring in such scenarios — not that they will inevitably happen. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う」は回答の「フォームクラスに `@AssertTrue` アノテーションを付けた `boolean` 型メソッドを追加して実装する」およびコード例に明確に含まれている |
| answer_relevancy | OK | 回答のすべての内容が相関バリデーションの実装方法という質問に直接関連している。@AssertTrueの使い方とコード例は質問への直接回答であり、実行順序に関する注意点と任意項目時のnull処理も相関バリデーション実装において必要な情報である。末尾の参照行（「参照: libraries-bean-validation.json:s11」）は出典の引用であり、質問と無関係な情報ではない。DeepEvalが指摘する「source file reference that did not contribute meaningful information」は、通常の引用表記であり回答の関連性を損なうものではない。 |
| faithfulness | OK | 回答の「どちらかが未入力のときにNullPointerExceptionなどの予期せぬ例外が発生しないよう、以下のように未入力チェックを追加すること」は、ナレッジの「予期せぬ例外が発生しないようにバリデーションのロジックを実装する必要がある」と一致している。「発生しないよう」という日本語表現は目的・防止を示しており、「例外が必ず発生する」とは述べていない。DeepEvalが「incorrectly states that a NullPointerException will occur」と判断したのは、「発生しないよう」という防止の表現を「発生する」という断言と誤読した偽陽性である。回答はナレッジの内容を正しく反映している。 |

### 参照事実（expected_facts）

- Jakarta Bean Validationの@AssertTrueを使って相関バリデーションを行う
