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