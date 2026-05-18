**結論**: メールアドレスと確認用メールアドレスの相関バリデーションは、使用するバリデーションフレームワーク（Nablarch ValidationまたはBean Validation）によって実装方法が異なります。

**根拠**:

### 方法1: Nablarch Validationを使う場合

BeanクラスにBeanクラスに `@ValidateFor` アノテーション付きのstaticメソッドを実装します。まず各項目のバリデーションを実行し、エラーがない場合に相関チェックを行います。

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
        // 各項目のバリデーション実施
        ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

        // 項目単体でエラーがあれば相関チェックしない
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

### 方法2: Bean Validation（Jakarta Bean Validation）を使う場合

`@AssertTrue` アノテーションを使って一致チェックメソッドを実装します。

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

任意項目の場合は未入力時の例外を防ぐため、nullチェックを追加します：

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true; // どちらかが未入力なら相関チェックしない
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

**注意点**:

- **Nablarch Validation**: 項目単体のバリデーション後にエラーがある場合は `if (!context.isValid()) return;` で相関チェックをスキップすること。これを忘れるとnullアクセス等の予期せぬ例外が発生する。
- **Bean Validation**: バリデーションの実行順序が保証されないため、項目単体のバリデーション前に相関バリデーションが呼ばれることがある。そのため、片方または両方が未入力の場合でも例外が発生しないようにロジックを実装する必要がある。
- **DBとの相関バリデーション（例: メールアドレスの重複チェック）**: Bean Validationでのデータベースアクセスはセキュリティ上のリスク（SQLインジェクション等）があるため、業務アクション側で実装すること。

参照: `component/libraries/libraries-nablarch-validation.json#s14`, `component/libraries/libraries-bean-validation.json#s11`