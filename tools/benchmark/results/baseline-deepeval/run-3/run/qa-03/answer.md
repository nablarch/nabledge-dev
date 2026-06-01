**結論**: ウェブアプリケーションでメールアドレスと確認用メールアドレスの相関バリデーションを実装するには、**Bean Validation** の `@AssertTrue` アノテーションを使う方法と、**Nablarch Validation** の `@ValidateFor` アノテーションを使う方法があります。

---

**根拠**:

#### Bean Validation を使う場合（推奨）

Form クラスにメソッドを追加し、`@AssertTrue` アノテーションを設定します。

```java
public class SampleForm {
    private String mailAddress;
    private String confirmMailAddress;

    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
        if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
            // どちらかが未入力の場合は相関バリデーションを実施しない（OKとする）
            return true;
        }
        return Objects.equals(mailAddress, confirmMailAddress);
    }
}
```

> **重要**: Bean Validation はバリデーションの実行順序を保証しないため、単項目バリデーション前に相関バリデーションが呼ばれる場合があります。未入力時に例外が発生しないよう、`null` や空文字のチェックを必ず入れてください。

コンポーネント設定ファイルに `BeanValidationStrategy` を定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### Nablarch Validation を使う場合

`@ValidateFor` アノテーションを付けた static メソッドで実装します。単項目バリデーション後にエラーがない場合のみ相関バリデーションを実行するのがポイントです。

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
        // まず単項目バリデーションを実施
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

#### 業務アクション（共通）

どちらの方式でも、`@InjectForm` + `@OnError` でバリデーションを起動します。

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "validate")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    SampleForm form = ctx.getRequestScopedVar("form");
    // バリデーション済みフォームを使って業務処理
}
```

---

**注意点**:
- `@OnError` アノテーションを設定しないと、バリデーションエラーがシステムエラー扱いになります。必ず設定してください。
- データベースと照合する相関バリデーション（例: メールアドレスの重複チェック）は Bean Validation 内で実装せず、業務アクション側で実施してください（バリデーション前の未検証値でDBアクセスするとSQLインジェクションリスクがあります）。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-nablarch-validation.json:s14