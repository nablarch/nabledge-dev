**結論**: ウェブアプリケーションで2つの入力項目の一致チェック（相関バリデーション）を行うには、フォームクラスに `@AssertTrue` アノテーションを付けたメソッドを定義し、`Objects.equals()` で2項目を比較する。

---

**根拠**:

`@AssertTrue` アノテーションをフォームのメソッドに付け、2つのフィールドを比較するロジックを実装する。

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

ウェブアプリケーションでBean Validationを使うには、コンポーネント設定ファイルに `BeanValidationStrategy` を定義し、アクションクラスに `@InjectForm` インターセプタを使用する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

---

**注意点**:

- Jakarta Bean Validationはバリデーションの実行順序を保証しないため、項目単体のバリデーションよりも前に相関バリデーションが呼び出される場合がある。そのため、相関バリデーション内で予期せぬ例外が発生しないようロジックを実装する必要がある。
- **任意項目の場合**（どちらかが未入力の可能性がある場合）は、未入力時にバリデーションをスキップする処理を追加すること。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない（バリデーションOKとする）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

---

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16