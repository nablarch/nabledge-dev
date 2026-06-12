**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、使用するバリデーション方式（Jakarta Bean Validation または Nablarch Validation）によって実装方法が異なります。

**根拠**:

### 方法1: Jakarta Bean Validation を使う場合

`@AssertTrue` アノテーションを付けたメソッドで2つの項目を比較します。

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

> **注意**: 項目単体のバリデーションより前に相関バリデーションが呼ばれる場合があります。どちらかが未入力の任意項目の場合は、null/空チェックを追加してください。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true; // 未入力の場合は相関バリデーションを実施しない
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

### 方法2: Nablarch Validation を使う場合

`@ValidateFor` アノテーションを付けた静的メソッド内で、まず項目単体のバリデーションを行ってからエラーがない場合に相関チェックを行います。

```java
public class SampleForm {

  @Domain(SampleDomain.MAIL)
  @Required
  public void setMailAddress(String mailAddress) { ... }

  @Domain(SampleDomain.MAIL)
  @Required
  public void setConfirmMailAddress(String confirmMailAddress) { ... }

  @ValidateFor("validate")
  public static void validate(ValidationContext<SampleForm> context) {
    ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

    if (!context.isValid()) {
      return; // 項目エラーがある場合は相関チェックしない
    }

    SampleForm form = context.createObject();
    if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
      context.addMessage("compareMailAddress"); // エラーメッセージを追加
    }
  }
}
```

**注意点**:
- **Jakarta Bean Validation**: バリデーション実行順序が保証されないため、任意項目の場合は null/空チェックを必ず追加すること
- **Nablarch Validation**: 項目単体のバリデーション後にエラーがなかった場合のみ相関チェックを行う設計が推奨パターン
- エラーメッセージは `compareMailAddress` などのメッセージIDで管理し、メッセージプロパティファイルに定義する

参照: `component/libraries/libraries-bean-validation.json#s11`, `component/libraries/libraries-nablarch-validation.json#s14`