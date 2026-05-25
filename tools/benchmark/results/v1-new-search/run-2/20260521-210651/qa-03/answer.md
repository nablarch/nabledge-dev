セクション内容を取得できました。Step 5〜7: 回答を生成して検証します。

---

**結論**: メールアドレスと確認用メールアドレスの一致チェックは、Bean Validationの場合は `@AssertTrue` 付きのbooleanゲッターで、Nablarch Validationの場合は `@ValidateFor` 付きのstaticメソッドで実装する。どちらも `@InjectForm` インターセプタを通じてウェブアプリケーションの入力チェックに組み込む。

**根拠**:

**Bean Validationを使う場合**

Formクラスにbooleanゲッターメソッドとして相関バリデーションを定義する。

```java
public class SampleForm {
    private String mailAddress;
    private String confirmMailAddress;

    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
        if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
            // どちらかが未入力の場合は、相関バリデーションは実施しない
            return true;
        }
        return Objects.equals(mailAddress, confirmMailAddress);
    }
}
```

コンポーネント設定ファイルに `BeanValidationStrategy` を定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Nablarch Validationを使う場合**

Formクラスにstaticメソッドとして定義し、項目単体バリデーション後に相関チェックを行う。

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
        // mailAddressとconfirmMailAddressのバリデーションを実施
        ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

        // エラーが発生した場合は相関バリデーションを実施しない
        if (!context.isValid()) {
            return;
        }

        // 相関バリデーション実施
        SampleForm form = context.createObject();
        if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
            context.addMessage("compareMailAddress");
        }
    }
}
```

**アクションへの組み込み（共通）**

`@InjectForm` と `@OnError` をアクションメソッドに設定する。

```java
@InjectForm(form = SampleForm.class, prefix = "form", validate = "validate")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション済みのフォームをリクエストスコープから取得する
    SampleForm form = ctx.getRequestScopedVar("form");
    // 以降の業務処理...
}
```

**注意点**:
- Bean Validationではバリデーションの実行順序が保証されない。そのため `@AssertTrue` メソッド内でまず未入力チェックを行い、未入力の場合は `true` を返して相関バリデーションをスキップすること。
- Bean ValidationのFormクラスのプロパティは全てString型で定義すること。String以外の型があると、不正な値の入力時にBean変換処理が失敗して予期せぬ例外が発生する。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, libraries-nablarch-validation.json:s14, handlers-InjectForm.json:s3

---