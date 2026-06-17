**結論**: ウェブアプリケーションでメールアドレスと確認用メールアドレスの一致チェックを行うには、Formクラスに `@AssertTrue` アノテーションを付けたメソッドを追加して相関バリデーションを実装します。

**根拠**:

**Formクラスの実装例**

```java
public class SampleForm {
  private String mailAddress;

  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      // どちらかが未入力の場合は相関バリデーションを実施しない（バリデーションOKとする）
      return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }

  // getter、setterは省略
}
```

**業務アクションの実装例**

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのformを使って業務処理を行う
}
```

**コンポーネント設定ファイル（Bean Validationの有効化）**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、単項目バリデーション（必須チェックなど）より先に相関バリデーションが実行される場合があります。未入力の場合に `NullPointerException` などが発生しないよう、必ず空チェックをした上で比較処理を行ってください。
- `@OnError` アノテーションを設定しないと、バリデーションエラーがシステムエラー扱いになるため必ず設定してください。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4