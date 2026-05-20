**結論**: ウェブアプリケーションの相関バリデーションは、FormクラスにBean Validationの `@AssertTrue` アノテーションを付けたメソッドを実装し、`InjectForm` インターセプタ経由で実行する。

**根拠**:

**① Formクラスに `@AssertTrue` で相関バリデーションを実装する**

メールアドレスと確認用メールアドレスの一致チェックは以下のように実装する。

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

**② コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**③ 業務アクションに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

**注意点**:
- Bean Validationではバリデーションの実行順序が保証されないため、相関バリデーションが項目単体バリデーションより先に呼ばれることがある。メールアドレスが任意項目の場合は、未入力時に例外が発生しないよう以下のようにnullチェックを行うこと。
  ```java
  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      return true; // どちらかが未入力の場合は相関バリデーションを実施しない
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }
  ```
- `@OnError` を設定しない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4