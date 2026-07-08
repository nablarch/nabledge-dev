**結論**: ウェブアプリケーションでの相関バリデーション（メールアドレスと確認用メールアドレスの一致チェック）は、Bean Validationを使用する場合は `@AssertTrue` アノテーションを付与したメソッドをFormクラスに定義することで実装します。Nablarch Validationを使用する場合は `@ValidateFor` アノテーションを付与した静的メソッドで実装します。

---

**根拠**:

#### Bean Validationを使用する場合（推奨）

Formクラスに `@AssertTrue` アノテーション付きのメソッドを定義します。

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

`message` プロパティに指定したメッセージID（`{compareMailAddress}`）が、バリデーションエラー時のメッセージとなります。

#### Nablarch Validationを使用する場合

`@ValidateFor` アノテーションを付与した静的メソッド内で相関バリデーションを実装します。

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
      // 単項目バリデーションを実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // 単項目でエラーが発生した場合は相関バリデーションをスキップ
      if (!context.isValid()) {
          return;
      }

      // 相関バリデーションを実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

---

**注意点**:

- **Bean Validationの実行順序**: Jakarta Bean Validationではバリデーションの実行順序が保証されないため、単項目バリデーションより前に相関バリデーションが呼ばれる場合があります。そのため、いずれかの項目が未入力の場合でも例外が発生しないよう実装する必要があります。

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

- **Formのプロパティ型**: Formクラスのプロパティは全て `String` 型で定義すること（Bean ValidationはBean変換後にバリデーションを実施するため）。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  相関バリデーションを行う
  ウェブアプリケーションのユーザ入力値のチェックを行う
  バリデーションルールの設定方法
- Nablarch Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-nablarch-validation.md
  相関バリデーションを行う