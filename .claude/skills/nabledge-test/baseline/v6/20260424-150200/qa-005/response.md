**結論**: 相関バリデーション（複数項目を組み合わせたバリデーション）には2つの実装方式があります。
1. **Nablarch Validation方式**: Beanクラスに `@ValidateFor` アノテーションを付けた static メソッドで実装し、`ValidationContext` にメッセージを追加する。
2. **Jakarta Bean Validation方式**: `@AssertTrue` アノテーションを付けたメソッドで真偽値を返す形で実装する。

データベースとの相関バリデーション（重複チェック等）は、上記のいずれでもなく、バリデーション済みの安全な値を使うために **業務アクション側**で実装する。

---

**根拠**:

■ Nablarch Validation方式（`@ValidateFor` + `ValidationContext`）

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
      // まず項目単体のバリデーションを実施
      ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

      // エラーが発生した場合は、相関バリデーションは実施しない
      if (!context.isValid()) {
          return;
      }

      // formオブジェクトを生成し、相関バリデーションを実施
      SampleForm form = context.createObject();
      if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
          // エラー時はメッセージIDをValidationContextに追加
          context.addMessage("compareMailAddress");
      }
  }
}
```

ポイント：
- まず `ValidationUtil.validate` で項目ごとのバリデーションを実施し、エラーがない場合のみ相関バリデーションを行う。
- エラー時は `context.addMessage("メッセージID")` でメッセージIDを明示的に追加する。

■ Jakarta Bean Validation方式（`@AssertTrue`）

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

任意項目の場合は、未入力時に相関バリデーションをスキップする実装が必要：

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true; // どちらかが未入力ならOK扱い
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

■ データベースとの相関バリデーション（業務アクション側で実装）

Bean Validationで DB アクセスを伴う相関バリデーションを行うと、バリデーション前の安全でない値でDBアクセスすることになり、SQLインジェクション等の脆弱性の原因となるため、**必ずバリデーション後の業務アクション側で実装**する。

業務アクションでエラーになった項目を画面上でハイライトしたい場合は、`ValidationUtil.createMessageForProperty` でメッセージを組み立て、`ApplicationException` を送出する。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

---

**注意点**:
- **Jakarta Bean Validation**ではバリデーションの実行順序は保証されない。項目単体のバリデーション前に相関バリデーションが呼ばれる可能性があるため、未入力等で例外が発生しない実装にする必要がある。
- **Nablarch Validation方式**では、先に `ValidationUtil.validate` で項目単体のバリデーションを実施し、`context.isValid()` がfalseなら相関バリデーションは実施しないのが定石。
- データベースアクセスを伴う相関バリデーションは Bean Validation や `@ValidateFor` ではなく、必ず業務アクション側で実装する（セキュリティ上の理由）。
- ラジオボタン等の選択値に応じてバリデーション項目を切り替えたい場合は `WebUtil.containsPropertyKeyValue` / `WebUtil.containsPropertyKey` を `@ValidateFor` メソッド内で使う。

参照:
- component/libraries/libraries-nablarch-validation.json#s14 (相関バリデーション - Nablarch Validation方式)
- component/libraries/libraries-nablarch-validation.json#s20 (DBとの相関バリデーションは業務アクションで実施)
- component/libraries/libraries-nablarch-validation.json#s16 (画面の入力値による条件分岐)
- component/libraries/libraries-bean-validation.json#s11 (相関バリデーション - @AssertTrue方式)
- component/libraries/libraries-bean-validation.json#s12 (DBとの相関バリデーションを業務アクションで行う理由)
- component/libraries/libraries-bean-validation.json#s13 (業務アクションでのエラーメッセージ構築)
