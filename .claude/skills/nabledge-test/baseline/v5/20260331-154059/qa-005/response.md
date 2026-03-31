**結論**: Nablarch 5 では、Bean Validation と Nablarch Validation の2つの方式で相関バリデーションを実装できます。Bean Validation（推奨）では `@AssertTrue` アノテーションを使用し、Nablarch Validation では `@ValidateFor` アノテーションを付けた static メソッドで実装します。

---

**根拠**:

## Bean Validation を使った相関バリデーション（推奨）

`@AssertTrue` アノテーションを使用して実装します。

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

## Nablarch Validation を使った相関バリデーション

`@ValidateFor` アノテーションを設定した static メソッド内で、以下の手順で実装します。

1. `ValidationUtil.validate()` で各項目のバリデーションを実施
2. `context.isValid()` でエラー確認し、エラーがある場合は相関バリデーションをスキップ
3. `context.createObject()` で Form を生成して複数項目を検証
4. エラーの場合は `context.addMessage("メッセージID")` でメッセージを追加

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

---

**注意点**:

- **Bean Validation の実行順序**: Bean Validation ではバリデーションの実行順序が保証されないため、項目単体のバリデーションよりも前に相関バリデーションが呼び出される場合があります。項目単体のバリデーションが実行されていない状態でも予期せぬ例外が発生しないよう実装してください。任意項目の場合、未入力時はバリデーションを実行せず `true` を返すようにしてください。

- **データベースとの相関バリデーション**: Bean Validation や Nablarch Validation でデータベースに対する相関バリデーションを実施しないでください。バリデーション実行中はオブジェクトの値の安全性が保証されないため、SQLインジェクション等の脆弱性の原因となります。データベースとの相関バリデーションは業務アクション側で実装してください（バリデーション済みの安全な値を使って DB アクセスするため）。

- **フォームクラスへの配置**: 相関バリデーションのロジックはフォームクラスに持たせるのが基本ですが、複数フォームクラスで共通となる場合は別クラスに抽出して共通化できます。

---

参照: `libraries-bean_validation.json#s1`, `libraries-nablarch_validation.json#s4`, `libraries-nablarch_validation.json#s10`, `libraries-bean_validation.json#s2`