Step 5〜7: 回答を生成し、検証します。

---

**結論**: Bean Validationの `@AssertTrue` アノテーションをFormクラスのgetterメソッドに付与して相関バリデーションを実装する。

**根拠**:

**1. Formクラスに `@AssertTrue` を実装する**

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

**2. コンポーネント定義ファイルに `BeanValidationStrategy` を設定する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**3. アクションクラスに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う。
}
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、相関バリデーションが項目単体バリデーションより先に呼び出される場合がある。そのため、未入力チェックなど予期せぬ例外が発生しないようにロジックを実装すること（上記コード例の `isNullOrEmpty` による早期リターン）。
- エラーメッセージ `{compareMailAddress}` はメッセージ定義ファイルにキー `compareMailAddress` で定義しておく必要がある。
- Formクラスのプロパティは全て `String` 型で定義すること。

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`

---