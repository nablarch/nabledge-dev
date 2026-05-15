**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、Jakarta Bean Validation の `@AssertTrue` アノテーションをFormクラスのメソッドに設定して実装します。

**根拠**:

Formクラスに `isXxx()` という boolean を返すメソッドを定義し、`@AssertTrue` を付与します。

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

エラーメッセージは `message` プロパティに指定したメッセージIDで定義します（例: `compareMailAddress=メールアドレスが一致しません。`）。

**注意点**:

Jakarta Bean Validation ではバリデーションの実行順序が保証されないため、**項目単体のバリデーション（必須チェック等）より前に相関バリデーションが呼び出される場合があります**。どちらかが未入力の状態でも例外が発生しないよう、以下のように null/空文字チェックを入れるべきです。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない（OKとする）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

参照: `libraries-bean-validation.json#s11`