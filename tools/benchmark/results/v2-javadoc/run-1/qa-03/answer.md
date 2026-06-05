Step 5〜7: 回答を生成し、検証します。

**結論**: `@AssertTrue` アノテーションをgetterメソッドに付けてメールアドレスと確認用メールアドレスの一致をチェックするのが、Bean Validationによる相関バリデーションの実装方法です。ウェブアプリケーションでは `@InjectForm` インターセプタと組み合わせて使用します。

**根拠**:

Formクラスに `@AssertTrue` アノテーションを使った相関バリデーションを実装します。

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

**任意項目の場合（未入力時に例外が発生しないよう対処が必要）**:

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は、相関バリデーションは実施しない
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

エラーメッセージはメッセージ管理のプロパティファイルで定義します（例: `compareMailAddress=メールアドレスが一致しません。`）。

業務アクションでは `@InjectForm` と `@OnError` を組み合わせます。

```java
@InjectForm(form = MailForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  MailForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのformを使って処理
}
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、相関バリデーションは項目単体のバリデーションよりも先に呼ばれる場合があります。そのため、nullや空文字チェックを行い、予期せぬ例外が発生しないようにする必要があります。
- Formクラスのプロパティは全て `String` 型で定義すること（Bean Validationの制約）。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3

---