Step 5-7: 回答を生成し、検証します。

**結論**: メールアドレスと確認用メールアドレスの一致チェック（相関バリデーション）は、Bean Validationを使う場合は `@AssertTrue` アノテーションで、Nablarch Validationを使う場合は `@ValidateFor` メソッド内で実装します。

---

**根拠**:

**Bean Validation（推奨）の場合**

Formクラスに `@AssertTrue` アノテーションを設定したbooleanメソッドを追加します。

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

**注意点（任意項目の場合）**: Bean Validationではバリデーションの実行順序が保証されないため、いずれかが未入力でも相関バリデーションが先に呼ばれる場合があります。任意項目の場合は未入力チェックを追加してください。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

**Nablarch Validation の場合**

`@ValidateFor` アノテーションを設定したメソッド内で、各項目のバリデーション後に相関チェックを実行します。

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
      // 各項目のバリデーションを先に実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // エラーが発生した場合は相関バリデーションを実施しない
      if (!context.isValid()) {
          return;
      }

      // formオブジェクトを生成し、相関バリデーションを実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

**注意点**:
- Bean Validationは、`@AssertTrue` を付けたメソッドの名前は `is` で始まる必要があります（booleanを返すgetter形式）。
- どちらの方式でも、エラーメッセージID（例: `compareMailAddress`）をプロパティファイルに定義する必要があります。
- Nablarch Validationでは、各項目のバリデーションが成功した後（`context.isValid()` がtrueの場合）にのみ相関バリデーションを実行する点が重要です。

参照: libraries-bean-validation.json:s11, libraries-nablarch-validation.json:s14