**結論**: ウェブアプリケーションで2項目の一致チェック（相関バリデーション）を行うには、Formクラスに `@AssertTrue` アノテーションを付けたgetterメソッドを実装します。

**根拠**:

FormクラスにBooleanを返すgetterを作成し、`@AssertTrue` を付与します。

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

エラーメッセージはpropertyファイルに `compareMailAddress` キーで定義します。

**任意項目の場合の注意点**: Jakarta Bean Validationはバリデーションの実行順序を保証しないため、単項目バリデーションより先に相関バリデーションが呼ばれる場合があります。メールアドレスが任意項目の場合、未入力時に `NullPointerException` が発生しないよう早期リターンが必要です。

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

ウェブアプリケーションでこのFormのバリデーションを実行するには、業務アクションメソッドに `@InjectForm` インターセプタを設定します。

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

また、コンポーネント設定ファイルに `BeanValidationStrategy` の定義が必要です。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Beanのプロパティは全て `String` 型で定義すること
- `@AssertTrue` を付けるgetterのメソッド名は `is` で始まる必要があります（Jakarta Bean Validationの仕様）
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いとなるため必ず設定すること

参照: libraries-bean-validation.json:s11, handlers-InjectForm.json:s3, libraries-bean-validation.json:s16