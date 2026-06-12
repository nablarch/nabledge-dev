**結論**: Formクラスに `@AssertTrue` アノテーションを付けたbooleanメソッドを実装することで、メールアドレスと確認用メールアドレスの相関バリデーションが実現できる。

**根拠**:

**1. Formクラスに相関バリデーションを実装する（Bean Validation）**

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

どちらかが未入力の場合は相関バリデーションをスキップする必要がある（後述の注意点を参照）。

**2. コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**3. アクションに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う。
}
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションよりも前に相関バリデーションが呼び出される場合がある。そのため、`mailAddress` や `confirmMailAddress` が未入力の場合でも予期せぬ例外が発生しないよう、以下のようにガード処理を入れること:

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

- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。
- Beanクラスのプロパティは全て `String` 型として定義すること。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4

---