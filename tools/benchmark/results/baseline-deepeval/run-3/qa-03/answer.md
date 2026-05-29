セクションの内容が揃いました。Step 5以降を実行します。

---

**結論**: `@AssertTrue` アノテーションを使った相関バリデーションメソッドをFormクラスに定義することで、メールアドレスと確認用メールアドレスの一致チェックを実装できます。

**根拠**:

Nablarch 6（Bean Validation）での実装例：

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

どちらかが任意項目（未入力を許容する）場合は、未入力時に相関バリデーションをスキップする処理が必要です：

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない（バリデーションOK）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

エラーメッセージは `message` プロパティのIDをキーにプロパティファイルに定義します：

```properties
compareMailAddress=メールアドレスと確認用メールアドレスが一致していません。
```

ウェブアプリでこのバリデーションを動かすには、業務アクションに `@InjectForm` を付けてBeanValidationStrategyをコンポーネント定義に設定します：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // ...
}
```

**注意点**:
- Bean Validationではバリデーションの実行順序は保証されないため、相関バリデーションが単項目バリデーションより先に呼ばれることがあります。そのため、`null`や空文字の場合でも例外が発生しないよう実装してください。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, libraries-bean-validation.json:s6

---