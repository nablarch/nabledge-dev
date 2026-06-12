Step 5〜8を実行します。

**結論**: メールアドレスと確認用メールアドレスの一致チェック（相関バリデーション）は、**Bean Validation**を使う場合は `@AssertTrue` アノテーションで、**Nablarch Validation**を使う場合は `@ValidateFor` メソッド内で実装します（Bean Validationの使用を推奨）。

---

**根拠**:

### Bean Validation（推奨）の場合

Formクラスに `@AssertTrue` アノテーションを付けたメソッドを定義します。

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

エラーメッセージはメッセージIDで定義します（例: `compareMailAddress=メールアドレスが一致しません。`）。

### Nablarch Validation の場合

`@ValidateFor` メソッド内で、単項目バリデーション後に相関チェックを実行します。

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
      // まず単項目バリデーションを実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // 単項目にエラーがある場合は相関バリデーションをスキップ
      if (!context.isValid()) {
          return;
      }

      // 相関バリデーション実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

**注意点**:
- Bean Validationでは実行順序が保証されないため、項目が任意項目の場合は相関バリデーション実行前に未入力チェックが必要です。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない（OKとする）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

- ウェブアプリケーションでBean Validationを使う場合は、`InjectForm` インターセプタと `BeanValidationStrategy` の設定が必要です。

参照: libraries-bean-validation.json:s11, libraries-nablarch-validation.json:s14

---