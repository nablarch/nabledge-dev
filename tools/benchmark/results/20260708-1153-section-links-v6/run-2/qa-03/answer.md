**結論**: `@AssertTrue` アノテーションをFormクラスのgetterメソッドに設定することで、メールアドレスと確認用メールアドレスが一致しているかを相関バリデーションで実装できます。

**根拠**:

Formクラスに `mailAddress` と `confirmMailAddress` フィールドを定義し、両者を比較するgetterに `@AssertTrue` を付けます。

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

ただし、Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体のバリデーションより先に相関バリデーションが呼び出される場合があります。どちらかが未入力の任意項目の場合は、nullチェックを行ってから比較してください。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は、相関バリデーションは実施しない。(バリデーションOKとする)
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

ウェブアプリケーションでBeanValidationを使用するには、コンポーネント設定ファイルに以下を定義し、業務アクションに `@InjectForm` と `@OnError` を設定します。

コンポーネント設定:
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

業務アクション:
```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  UserForm form = ctx.getRequestScopedVar("form");
  // formを元に業務処理を行う。
}
```

**注意点**: Formクラスのプロパティは全て `String` 型で定義してください。String以外の型が存在する場合、バリデーション実施前の変換処理が失敗し、予期せぬ例外が発生することがあります。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  相関バリデーションを行う
  ウェブアプリケーションのユーザ入力値のチェックを行う
  バリデーションルールの設定方法
- InjectForm インターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md
  InjectFormを使用する
  バリデーションエラー時の遷移先を指定する