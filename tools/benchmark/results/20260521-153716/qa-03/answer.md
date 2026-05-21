Step 5：回答を生成します。

`sections_content` から回答を作成します。

**結論**: ウェブアプリケーションでメールアドレスと確認用メールアドレスの一致チェックは、FormクラスにJakarta Bean Validationの `@AssertTrue` アノテーションを付けたメソッドとして実装します。

**根拠**:

Formクラスに以下のように実装します:

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

**検証ステップ (Step 6):**

- `@AssertTrue` アノテーション → s11に明記されている → 支持されている
- `Objects.equals(mailAddress, confirmMailAddress)` → s11のコード例に直接記載 → 支持されている
- バリデーション実行順序の注意点 → s11のImportantに明記 → 支持されている
- `StringUtil.isNullOrEmpty` による任意項目の対応 → s11のコード例に記載 → 支持されている
- `BeanValidationStrategy` 設定 → s16に記載 → 支持されている
- `@InjectForm` インターセプタ → s16およびs3に記載 → 支持されている

**verify_result = PASS**

**final_answer = answer_text**

---

**結論**: ウェブアプリケーションで2項目の一致チェック（相関バリデーション）は、Formクラスに `@AssertTrue` アノテーションを付けたメソッドを実装することで実現します。

**根拠**:

Formクラスに以下のように相関バリデーションメソッドを実装します:

```java
public class SampleForm {
  private String mailAddress;
  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    return Objects.equals(mailAddress, confirmMailAddress);
  }

  // getter、setterは省略
}
```

メールアドレスが任意入力の場合は、未入力時に例外が発生しないよう以下のように実装します:

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    // どちらかが未入力の場合は、相関バリデーションは実施しない（OKとする）
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

エラーメッセージ `{compareMailAddress}` は、メッセージプロパティファイルに定義します:

```properties
compareMailAddress=メールアドレスが一致していません。
```

ウェブアプリケーションでBean Validationを使用するには、コンポーネント設定ファイルへの設定と、業務アクションメソッドへの `@InjectForm` アノテーション付与が必要です:

コンポーネント設定ファイル:
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

業務アクションの例:
```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // 業務処理
}
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、項目単体バリデーションより先に相関バリデーションが呼ばれる場合がある。未入力の場合に予期せぬ例外が発生しないようロジックを実装すること。
- `@OnError` アノテーションを業務アクションメソッドに設定しない場合、バリデーションエラーがシステムエラー扱いになるため注意すること。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3

---