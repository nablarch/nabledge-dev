**結論**: FormクラスにJakarta Bean Validationの`@AssertTrue`アノテーションを付けたメソッドを定義することで、メールアドレスと確認用メールアドレスの相関バリデーションを実装できる。

**根拠**:

Formクラスでの実装例:

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

任意項目の場合（どちらかが未入力のときは相関チェックをスキップ）:

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

エラーメッセージ定義（プロパティファイル）:

```properties
compareMailAddress=メールアドレスと確認用メールアドレスが一致しません。
```

ウェブアプリケーションでBean Validationを使用するためのコンポーネント設定:

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

業務アクションでの`@InjectForm`使用例:

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのformを使って業務処理を行う。
}
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体バリデーション前に相関バリデーションが呼ばれる場合がある。メールアドレスが任意項目の場合は、`StringUtil.isNullOrEmpty`でnull/空チェックを入れてから比較すること。
- `@OnError`アノテーションが設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4