**結論**: Nablarch 6 での相関バリデーション（複数項目を使った検証）は、用途によって実装方法が異なります。

1. **Jakarta Bean Validation** を使う場合: フォームクラスに `@AssertTrue` を付けた判定メソッドを実装する。
2. **Nablarch Validation** を使う場合: Bean クラスに `@ValidateFor` アノテーションを付けた static メソッドを実装し、その中で `ValidationUtil` と `ValidationContext` を使って相関チェックを行う。
3. **データベースとの相関バリデーション** は、SQL インジェクション等のリスクを避けるため Form 側ではなく **業務アクション側** で実装する。

---

**根拠**:

### 1. Bean Validation (`@AssertTrue`) による相関バリデーション

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

Jakarta Bean Validation では実行順序が保証されないため、単項目バリデーション前に相関バリデーションが呼び出されても予期せぬ例外が発生しないようにする必要があります。任意項目の場合は未入力時に `true` を返してスキップします。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true;  // どちらかが未入力なら相関チェックは行わない
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

### 2. Nablarch Validation (`@ValidateFor`) による相関バリデーション

項目ごとのバリデーションを先に実行し、エラーがない場合にのみ相関バリデーションを実行します。エラー時は `ValidationContext#addMessage` でメッセージ ID を追加します。

```java
public class SampleForm {
  @Domain(SampleDomain.MAIL) @Required
  public void setMailAddress(String mailAddress) { this.mailAddress = mailAddress; }

  @Domain(SampleDomain.MAIL) @Required
  public void setConfirmMailAddress(String confirmMailAddress) { this.confirmMailAddress = confirmMailAddress; }

  @ValidateFor("validate")
  public static void validate(ValidationContext<SampleForm> context) {
      // まず項目ごとのバリデーションを実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // エラーがあれば相関バリデーションは実施しない
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

### 3. データベースとの相関バリデーション

データベースとの相関バリデーションは **業務アクションで** 実装します。業務アクション側で ApplicationException を送出し、画面の該当項目をエラーとしてハイライトしたい場合は `ValidationUtil#createMessageForProperty` を使います。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

---

**注意点**:

- **Bean Validation** では実行順序が保証されないため、相関バリデーションは単項目チェック前に呼ばれても NPE 等が発生しないよう防御的に実装すること。
- **Nablarch Validation** では逆に、相関バリデーションの前に `ValidationUtil.validate` で項目ごとのバリデーションを実行し、`context.isValid()` でエラーがない場合のみ相関バリデーションを行う流れが基本。
- **DB を参照する相関バリデーション** は、バリデーション前の未検証の値で DB アクセスすると SQL インジェクション等の脆弱性になるため、必ずバリデーション済みの値を使える業務アクション側で実装すること。
- Nablarch Validation では `WebUtil.containsPropertyKeyValue` / `WebUtil.containsPropertyKey` を使って、ラジオボタン等の選択値に応じて相関バリデーション対象項目を切り替えることもできる。

参照:
- `component/libraries/libraries-bean-validation.json#s11` (Bean Validation 相関バリデーション)
- `component/libraries/libraries-bean-validation.json#s12` (DB との相関バリデーションは業務アクションで)
- `component/libraries/libraries-bean-validation.json#s13` (ApplicationException でのエラー表示)
- `component/libraries/libraries-nablarch-validation.json#s14` (Nablarch Validation 相関バリデーション)
- `component/libraries/libraries-nablarch-validation.json#s16` (条件による対象切り替え)
- `component/libraries/libraries-nablarch-validation.json#s20` (DB との相関バリデーションは業務アクションで)
