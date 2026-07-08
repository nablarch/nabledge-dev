**結論**: ウェブアプリケーションでメールアドレスと確認用メールアドレスの相関バリデーションを行うには、FormクラスにJakarta Bean Validationの `@AssertTrue` アノテーションを使ったメソッドを定義する。

**根拠**:

Formクラスに相関バリデーションメソッドを実装する。`isEqualsMailAddress()` のような `is` で始まるboolean型メソッドに `@AssertTrue` を設定し、一致チェックのロジックを記述する。

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

ウェブアプリケーションでは、業務アクションメソッドに `@InjectForm` と `@OnError` を設定することでバリデーションが自動実行される。

```java
@InjectForm(form = UserForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  UserForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのformを使って業務処理
}
```

**注意点**:

Jakarta Bean Validationはバリデーションの実行順序を保証しないため、項目単体のバリデーション（必須チェック等）より前に相関バリデーションが呼び出される場合がある。どちらかが未入力の場合は例外が発生しないよう、以下のように実装すること。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は相関バリデーションを実施しない（バリデーションOKとする）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

エラーメッセージ `{compareMailAddress}` はメッセージプロパティファイルで定義する（例: `compareMailAddress=メールアドレスと確認用メールアドレスが一致していません。`）。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  相関バリデーションを行う
  ウェブアプリケーションのユーザ入力値のチェックを行う
- InjectForm インターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md
  InjectFormを使用する