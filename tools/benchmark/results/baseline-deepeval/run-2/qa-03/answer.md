これで回答の生成に必要な情報が揃いました。Step 5〜8を実行します。

---

**結論**: ウェブアプリケーションでの相関バリデーション（メールアドレス一致チェック）は、FormクラスにJakarta Bean Validationの `@AssertTrue` アノテーションを付けたメソッドを定義することで実装します。

**根拠**:

Formクラスに `@AssertTrue` アノテーションを付けたbooleanメソッドを定義します。メソッド名は `is` で始める必要があります。

```java
public class SampleForm {
    private String mailAddress;

    private String confirmMailAddress;

    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
        return Objects.equals(mailAddress, confirmMailAddress);
    }
    // getter、setterは省略
}
```

エラーメッセージは `message` 属性で指定したメッセージIDをプロパティファイルに定義します。

```properties
compareMailAddress=メールアドレスと確認用メールアドレスが一致していません。
```

ウェブアプリケーションでこのバリデーションを動かすには、`@InjectForm` インターセプタと `BeanValidationStrategy` を組み合わせます。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    SampleForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

**注意点**:

Jakarta Bean Validationではバリデーションの実行順序が保証されないため、**項目単体のバリデーションより先に相関バリデーションが呼び出される場合があります**。mailAddress や confirmMailAddress が任意項目の場合、未入力時に `NullPointerException` が発生しないよう、以下のように null/空チェックを入れてください。

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

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`

---