### Answer

ウェブアプリケーションでメールアドレスと確認用メールアドレスの相関バリデーションを実装する方法を説明します。

---

## Jakarta Bean Validation を使う場合

Formクラスに `@AssertTrue` アノテーションを付けたメソッドを実装します。

```java
public class SampleForm {
  private String mailAddress;
  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      // どちらかが未入力の場合は相関バリデーションを実施しない（OKとして返す）
      return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }
}
```

**重要な注意点：** Jakarta Bean Validationはバリデーションの実行順序を保証しません。項目単体のバリデーションより先に相関バリデーションが呼ばれる場合があるため、`mailAddress` や `confirmMailAddress` が未入力（null/空）のケースでも例外が発生しないようにガード処理を入れてください。

ウェブアプリケーションでBean Validationを使用するには、コンポーネント設定ファイルに以下を定義する必要があります（`InjectForm` インターセプタ経由で実行されます）。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

---

## Nablarch Validation を使う場合

Formクラスに `@ValidateFor` アノテーションを付けたstaticメソッドで実装します。**項目単体のバリデーションを先に実行し、エラーがなければ相関バリデーションを実行する**流れになります。

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

    // 項目単体でエラーがあれば相関バリデーションは実施しない
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

Nablarch Validationでは実行順序が明示的にコントロールできるため、「項目単体バリデーション → 相関バリデーション」の順序を確実に保証できます。

---

## DBとの相関バリデーション（補足）

「メールアドレスがDB上で重複していないか」のようなデータベースを使った相関バリデーションは、Formクラスではなく**業務アクション側**で実装してください。Bean Validation実行中の値は安全性が保証されていないため、SQLインジェクション等の脆弱性防止のためにバリデーション済みの値でDBアクセスする必要があります。