**結論**: 会員登録画面でメールアドレスと確認用メールアドレスの相関バリデーションを行うには、Bean Validation の `@AssertTrue` アノテーションを使ったメソッドをFormクラスに追加します。

**根拠**:

Bean Validation（推奨）を使う場合、Formクラスに `@AssertTrue` アノテーション付きのメソッドを定義します。

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

エラーメッセージは `message` プロパティに指定したメッセージIDから取得されます。

ウェブアプリケーションで Bean Validation を使用するには、コンポーネント設定ファイルに以下を定義する必要があります。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:

- **バリデーション実行順序は保証されない**: Jakarta Bean Validation では、項目単体のバリデーション（`@NotNull` など）より先に相関バリデーションが呼ばれる場合があります。そのため、項目が任意項目（未入力可）の場合は、`null` や空文字のチェックを先に行わないと予期せぬ例外が発生します。

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

- 会員登録画面ではメールアドレスが必須項目になることが多いですが、任意の場合はこのガードが必要です。

参照: knowledge/component/libraries/libraries-bean-validation.json#s11, knowledge/component/libraries/libraries-bean-validation.json#s16