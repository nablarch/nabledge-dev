**結論**: `@AssertTrue` アノテーションを使用したメソッドをFormクラスに定義し、`Objects.equals()` で2項目を比較する。ウェブアプリケーションでは `@InjectForm` インターセプタ経由でバリデーションが実行される。

**根拠**:

相関バリデーションは、FormクラスにbooleanメソッドとJakarta Bean Validationの `@AssertTrue` アノテーションを組み合わせて実装する。

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

メールアドレスが任意項目（未入力を許容する）の場合は、どちらかが未入力のときに相関バリデーションをスキップする必要がある。

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

ウェブアプリケーションでバリデーションを実行するには、業務アクションのメソッドに `@InjectForm` を設定する。

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う
}
```

Bean Validationを `@InjectForm` で使用するには、コンポーネント設定ファイルに以下の設定が必要。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されない。項目単体のバリデーション（`@Required`など）より前に相関バリデーションが実行される場合があるため、相関バリデーションメソッド内で予期せぬ例外が発生しないよう実装すること。
- `@OnError` を `@InjectForm` と合わせて設定しないと、バリデーションエラーがシステムエラー扱いになる。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3