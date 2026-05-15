**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、使用するバリデーションライブラリによって実装方法が異なります。

**根拠**:

### Jakarta Bean Validation を使用する場合

Formクラスに `@AssertTrue` アノテーションを付けたメソッドを実装します。

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

任意項目の場合は、どちらかが未入力のときに例外が発生しないよう null チェックが必要です。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

### Nablarch Validation を使用する場合

Beanクラスに `@ValidateFor` アノテーションを付けた静的メソッドを実装します。まず各項目のバリデーションを実行し、エラーがなければ相関チェックを行います。

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
      return;
    }
    SampleForm form = context.createObject();
    if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
      context.addMessage("compareMailAddress");
    }
  }
}
```

**注意点**:
- Bean Validation: バリデーションの実行順序は保証されません。項目単体のバリデーション（必須チェック等）より先に相関バリデーションが呼ばれる場合があるため、nullや空文字を考慮した実装が必要です。
- Nablarch Validation: 項目単体バリデーションのエラー有無を `context.isValid()` で確認してから相関チェックに進むのが定石です。エラーメッセージIDは `context.addMessage()` で明示的に追加します。

参照: component/libraries/libraries-bean-validation.json#s11, component/libraries/libraries-nablarch-validation.json#s14