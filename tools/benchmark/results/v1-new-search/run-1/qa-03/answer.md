Step 5〜7: 回答を生成し、verify を実行します。

**結論**: ウェブアプリケーションで2項目の一致チェックをする相関バリデーションは、Bean Validation を使う場合は `@AssertTrue` アノテーション付きメソッドで実装し、Nablarch Validation を使う場合は `@ValidateFor` アノテーション付きの static メソッドで `ValidationContext` にメッセージを追加して実装します。

**根拠**:

### Bean Validation を使う場合

FormクラスにBooleanを返すメソッドを定義し、`@AssertTrue` を付けます。

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

コンポーネント設定ファイルに `BeanValidationStrategy` を定義し、InjectForm インターセプタと連携させます。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

業務アクションには `@InjectForm` と `@OnError` を設定します。

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

エラーメッセージは `compareMailAddress` というメッセージIDでメッセージ管理に定義します。

### Nablarch Validation を使う場合

FormクラスにValidation実行用 static メソッドを定義し、`@ValidateFor` を付けます。

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

ウェブアプリケーションでは同様に InjectForm インターセプタを使ってバリデーションを起動します。

**注意点**:
- Bean Validation では実行順序が保証されないため、**相関バリデーションが項目単体バリデーションより先に呼ばれる場合がある**。各項目が任意入力の場合は、未入力時に例外が発生しないよう `isNullOrEmpty` チェックを必ず入れること。
- Nablarch Validation では先に `ValidationUtil.validate` で各項目のバリデーションを行い、`context.isValid()` がfalseの場合は相関バリデーションをスキップすることで、安全に実装できる。
- FormクラスのプロパティはすべてString型で定義すること（Bean Validationの場合）。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, libraries-nablarch-validation.json:s14, handlers-InjectForm.json:s3

---