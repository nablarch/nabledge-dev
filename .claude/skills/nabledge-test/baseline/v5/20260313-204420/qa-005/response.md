**結論**: 相関バリデーションの実装方法は、使用しているバリデーション機能（Bean Validation または Nablarch Validation）によって異なります。

---

## Bean Validation を使用する場合

`@AssertTrue` アノテーションを使用してフォームクラスに相関バリデーションメソッドを実装します。

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

> **重要注意点**: Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションよりも前に相関バリデーションが呼び出される場合がある。任意項目の場合、未入力時はバリデーションを実行せず `true` を返すこと。

---

## Nablarch Validation を使用する場合

`@ValidateFor` アノテーションを付与した static メソッドで実装します。

実装手順:
1. `ValidationUtil.validate()` で各項目のバリデーションを実施
2. `context.isValid()` でエラー確認し、エラーがある場合は相関バリデーションをスキップ
3. `context.createObject()` で Form を生成して複数項目を検証
4. 相関バリデーションエラーの場合は `context.addMessage("メッセージID")` でメッセージを追加

```java
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
```

**使用クラス**: `nablarch.core.validation.ValidationContext`、アノテーション: `@ValidateFor`

---

**注意点**:
- **データベースとの相関バリデーション**（例: 重複チェック）は業務アクション側で実装すること。
- Nablarch Validation では `@ValidateFor` メソッド内で `context.isValid()` チェックを行い、単項目バリデーションにエラーがある場合は相関バリデーションをスキップするのが推奨パターン。

参照: `libraries-bean_validation.json#s1`、`libraries-nablarch_validation.json#s4`、`libraries-nablarch_validation.json#s10`、`libraries-bean_validation.json#s2`
