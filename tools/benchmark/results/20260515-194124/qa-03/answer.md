**結論**: 相関バリデーション（メールアドレスと確認用メールアドレスの一致チェック）は、Bean ValidationとNablarch Validationの2つの方法で実装できます。Nablarch 6 では **Bean Validation（`@AssertTrue`）** を使うのが標準的なアプローチです。

**根拠**:

### Bean Validation を使う方法（推奨）

`@AssertTrue` アノテーションを付けたメソッドをFormクラスに定義します。

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

メソッド名は `is` で始める必要があります（JavaBeansの慣習）。`message` プロパティにエラーメッセージのキーを指定します。

### Nablarch Validation を使う方法

`@ValidateFor` アノテーションを付けた静的メソッドで実装します。項目単体のバリデーション後に相関バリデーションを実行する点が特徴です。

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
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      if (!context.isValid()) {
          return;
      }

      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

**注意点**:

1. **Bean Validation では実行順序が保証されない**: 項目単体のバリデーションより前に相関バリデーションが呼ばれることがあります。任意項目の場合、未入力時に予期せぬ例外が発生しないよう、`null` チェックを必ず行ってください。

    ```java
    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
      if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true;
      }
      return Objects.equals(mailAddress, confirmMailAddress);
    }
    ```

2. **データベースとの相関バリデーションは業務アクション側で実装すること**: Bean Validation実行中はオブジェクトの値が安全である保証がないため、DBを使う相関バリデーションはバリデーション後の業務アクションで行います。

参照: `component/libraries/libraries-bean-validation.json#s11`, `component/libraries/libraries-bean-validation.json#s12`, `component/libraries/libraries-nablarch-validation.json#s14`