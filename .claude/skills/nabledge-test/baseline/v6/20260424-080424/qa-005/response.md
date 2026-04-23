**結論**: Nablarch 6 における相関バリデーション（複数項目を使用したバリデーション）の実装方法は、使用するバリデーションライブラリ（Jakarta Bean Validation / Nablarch Validation）によって異なります。また、データベースとの相関バリデーションは、ライブラリ内では行わず、**業務アクション側で実装する**必要があります。

**根拠**:

### 1. Jakarta Bean Validation による相関バリデーション

`@AssertTrue` アノテーションを使用して実装します。

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

### 2. Nablarch Validation による相関バリデーション

Bean クラスの `@ValidateFor` アノテーションを設定したメソッドで実装します。まず項目ごとのバリデーションを実施し、エラーが発生しなかった場合にのみ相関バリデーションを実行するのがポイントです。エラー時は `ValidationContext` にメッセージ ID を明示的に追加します。

```java
public class SampleForm {

  @Domain(SampleDomain.MAIL)
  @Required
  public void setMailAddress(String mailAddress) { this.mailAddress = mailAddress; }

  @Domain(SampleDomain.MAIL)
  @Required
  public void setConfirmMailAddress(String confirmMailAddress) { this.confirmMailAddress = confirmMailAddress; }

  @ValidateFor("validate")
  public static void validate(ValidationContext<SampleForm> context) {
      // 項目単体のバリデーションを先に実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // エラーが発生した場合は、相関バリデーションを実施しない
      if (!context.isValid()) {
          return;
      }

      // formオブジェクトを生成し、相関バリデーションを実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          context.addMessage("compareMailAddress");
      }
  }
}
```

**注意点**:

- **Jakarta Bean Validation ではバリデーションの実行順序が保証されない**ため、項目単体のバリデーションよりも前に相関バリデーションが呼び出される場合があります。任意項目で未入力となりうる値を扱う場合は、未入力時に `return true;` で早期リターンするなど、予期せぬ例外が発生しないようロジックを実装する必要があります。

  ```java
  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      return true; // 未入力時はバリデーションOKとする
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }
  ```

- **データベースとの相関バリデーションは業務アクション側で実装する**こと（Bean Validation / Nablarch Validation のどちらも同様）。Bean Validation 実行中のオブジェクト値はバリデーション実施前の安全ではない値であり、そのままデータベースアクセスに使用すると SQL インジェクション等の脆弱性の原因となるためです。バリデーション実行後の業務アクション側で実施することで、安全な値でデータベースへアクセスできます。

- Nablarch Validation では、`@ValidateFor` メソッド内で先に `ValidationUtil.validate(...)` で項目単体バリデーションを実施し、`context.isValid()` でエラーがないことを確認してから相関バリデーションに進むのが定石です。

参照:
- `component/libraries/libraries-bean-validation.json#s11` (相関バリデーションを行う)
- `component/libraries/libraries-bean-validation.json#s12` (データベースとの相関バリデーションを行う)
- `component/libraries/libraries-nablarch-validation.json#s14` (相関バリデーションを行う)
- `component/libraries/libraries-nablarch-validation.json#s20` (データベースとの相関バリデーションを行う)
