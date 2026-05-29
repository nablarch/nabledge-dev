**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、Bean Validationを使う場合は`@AssertTrue`アノテーション付きのメソッドで実装し、Nablarch Validationを使う場合は`@ValidateFor`アノテーション付きのstaticメソッドで実装する。どちらの方式でも、ウェブアプリケーションでは`@InjectForm`インターセプタを使ってバリデーションを実行する。

---

**根拠**:

#### Bean Validation を使う場合

Formクラスに`@AssertTrue`を付けたメソッドを実装する。

```java
public class SampleForm {
  private String mailAddress;
  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      // どちらかが未入力の場合は、相関バリデーションは実施しない。(バリデーションOKとする)
      return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }
}
```

業務アクションに`@InjectForm`と`@OnError`を設定する。

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

コンポーネント設定ファイルに`BeanValidationStrategy`を定義する（Bean Validationを使う場合に必要）。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

---

#### Nablarch Validation を使う場合

Formクラスに`@ValidateFor`を付けたstaticメソッドで実装する。まず項目ごとのバリデーションを実施し、エラーがなければ相関バリデーションを実行する。

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
      // mailAddressとconfirmMailAddressのバリデーションを実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // エラーが発生した場合は、相関バリデーションを実施しない
      if (!context.isValid()) {
          return;
      }

      // formオブジェクトを生成し、相関バリデーションを実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          // mailAddressとconfirmMailAddressが一致していない場合エラー
          context.addMessage("compareMailAddress");
      }
  }
}
```

業務アクションへの`@InjectForm`設定はBean Validationと同様。

---

**注意点**:
- **Bean Validationの実行順序**: Jakarta Bean Validationではバリデーションの実行順序は保証されないため、項目単体のバリデーションより前に相関バリデーションが呼び出される場合がある。任意項目の場合は、未入力時に`true`を返してバリデーションをスキップするロジックが必要。
- **`@OnError`の設定必須**: `@OnError`が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため注意。
- **Nablarch Validationの順序保証**: `@ValidateFor`メソッド内では`context.isValid()`で項目単体バリデーションのエラー有無を確認してから相関バリデーションを実行することで、安全な実装が可能。

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `libraries-nablarch-validation.json:s14`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`

---