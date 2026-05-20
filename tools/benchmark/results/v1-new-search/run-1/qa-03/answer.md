**結論**: ウェブアプリケーションでメールアドレスと確認用メールアドレスの相関バリデーションは、Formクラスに `@AssertTrue` アノテーションを付けたbooleanメソッドを実装することで行う。

**根拠**:

FormクラスのgetterメソッドにJakarta Bean Validationの `@AssertTrue` を使用する。

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

`message` 属性に指定したキー（例: `compareMailAddress`）でエラーメッセージをプロパティファイルに定義する。

両項目が任意入力の場合は、どちらかが未入力のときにバリデーションをスキップする実装が必要:

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

ウェブアプリケーションでは、アクションメソッドに `@InjectForm` インターセプタを設定することでバリデーションが実行される:

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    SampleForm form = ctx.getRequestScopedVar("form");
    // ...
}
```

コンポーネント設定ファイルで `BeanValidationStrategy` を設定しておく必要がある:

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、単項目バリデーションより前に相関バリデーションが実行される場合がある。未入力・null値でも例外が発生しないよう実装すること。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3