**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、使用するバリデーション方式によって2通りの実装方法があります。

**根拠**:

### 方法1: Jakarta Bean Validation を使う場合（推奨）

`@AssertTrue` アノテーションを付けたメソッドを Form クラスに追加します。

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

両項目が任意入力（未入力を許容）の場合は、未入力時にスキップする処理が必要です。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        // どちらかが未入力の場合は相関バリデーションを実施しない
        return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

### 方法2: Nablarch Validation を使う場合

`@ValidateFor` アノテーションを付けた static メソッドを Form クラスに追加します。まず項目単体のバリデーションを実施し、エラーがなければ相関バリデーションを行います。

```java
public class SampleForm {

    @Domain(SampleDomain.MAIL)
    @Required
    public void setMailAddress(String mailAddress) { ... }

    @Domain(SampleDomain.MAIL)
    @Required
    public void setConfirmMailAddress(String confirmMailAddress) { ... }

    @ValidateFor("validate")
    public static void validate(ValidationContext<SampleForm> context) {
        // 項目単体のバリデーション
        ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

        // エラーがあれば相関バリデーションはスキップ
        if (!context.isValid()) {
            return;
        }

        // 相関バリデーション
        SampleForm form = context.createObject();
        if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
            context.addMessage("compareMailAddress");
        }
    }
}
```

**注意点**:

- **Bean Validation の実行順序**: Jakarta Bean Validation では、項目単体のバリデーションよりも先に `@AssertTrue` の相関バリデーションが呼ばれる場合があります。未入力・不正値でも例外が発生しないよう実装してください。
- **データベースとの相関バリデーション**: DBアクセスを伴う相関バリデーション（例: 登録済みメールアドレスの重複チェック）は、Bean Validation / Nablarch Validation のどちらでも**業務アクション側**で実装してください。バリデーション実行中の値は安全性が保証されず、SQLインジェクション等の脆弱性につながるためです。

参照: `component/libraries/libraries-bean-validation.json#s11`, `component/libraries/libraries-nablarch-validation.json#s14`