**結論**: Bean Validationでは `@AssertTrue` アノテーションをgetterメソッドに設定することで相関バリデーションを実装する。Nablarch Validationでは `@ValidateFor` メソッド内で項目単体バリデーション後に相関チェックを実装する。

**根拠**:

**Bean Validationを使う場合（推奨）**

FormクラスのgetterメソッドにJakarta Bean Validationの `@AssertTrue` アノテーションを設定する。

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

> **注意**: Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションより前に相関バリデーションが呼び出される場合がある。両項目が任意入力の場合は、未入力時にバリデーションをスキップする実装が必要。

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

ウェブアプリケーションでBean Validationを使うには、コンポーネント設定ファイルに以下を追加する。

```xml
<component name="validationStrategy"
    class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Nablarch Validationを使う場合**

`@ValidateFor` アノテーションを設定したバリデーションメソッド内で、項目単体のバリデーション後に相関チェックを実装する。

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
      // まず項目単体のバリデーションを実施
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
- ウェブアプリケーションでのバリデーション実行は `InjectForm` インターセプタを経由して行う
- データベースとの相関バリデーション（例：メールアドレスの重複チェック）は、SQLインジェクション防止の観点から業務アクション側で実装すること
- Bean Validationではバリデーション実行順序が不定のため、相関バリデーション内で予期せぬ例外が発生しないよう実装すること

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, libraries-nablarch-validation.json:s14