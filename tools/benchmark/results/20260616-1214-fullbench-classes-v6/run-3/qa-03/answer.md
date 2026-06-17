**結論**: フォームクラスに `@AssertTrue` アノテーションを付けた `boolean` 型メソッドを追加して実装する。

**根拠**:

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

メソッドが `false` を返した場合、`message` 属性に指定したメッセージID `{compareMailAddress}` のメッセージがエラーとして通知される。

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションより前に相関バリデーションが呼び出される場合がある。
- `mailAddress` や `confirmMailAddress` が任意項目の場合、どちらかが未入力のときに `NullPointerException` などの予期せぬ例外が発生しないよう、以下のように未入力チェックを追加すること。

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

参照: libraries-bean-validation.json:s11