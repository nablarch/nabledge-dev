**結論**: ウェブアプリケーションでの相関バリデーションは、Formクラスに `@AssertTrue` アノテーションを付けたメソッドを追加することで実装できます（Bean Validation使用）。

**根拠**:

**Bean Validationを使う場合（推奨）**

Formクラスに `@AssertTrue` アノテーションを付けたbooleanメソッドを実装します。

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

任意項目の場合（どちらかが未入力の場合がある場合）は、以下のように `null` / 空文字チェックを追加してください：

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は、相関バリデーションは実施しない。(バリデーションOKとする)
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

**コンポーネント設定**（Bean Validationをウェブアプリで使うために必要）：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**業務アクションへの組み込み**：

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

---

**Nablarch Validationを使う場合の代替実装**

`@ValidateFor` を付けた staticメソッドで、項目単体のバリデーション後に相関バリデーションを実施します：

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

**注意点**:
- Bean Validationではバリデーションの実行順序が保証されないため、相関バリデーションが項目単体バリデーションより先に呼ばれる場合があります。必ず `null` / 空文字の場合を考慮した実装にしてください。
- `@OnError` アノテーションが設定されていない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定してください。

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `libraries-nablarch-validation.json:s14`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`