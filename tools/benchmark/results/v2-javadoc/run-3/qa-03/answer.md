必要なセクションがすべて揃いました。Step 4の確認：

**selected_pages** (選択理由):
- `component/libraries/libraries-bean-validation.json` — Bean Validationで相関バリデーションを実装するための主要ドキュメント
- `component/handlers/handlers-InjectForm.json` — ウェブアプリケーションでのバリデーション実行方法

**read_sections**: s11, s12, s16 (Bean Validation), s3, s4 (InjectForm)

Step 5: 回答生成

Step 6 (verify):
- `@AssertTrue` アノテーションを使う → s11に明示あり ✅
- `Objects.equals()` を使う → s11のコード例に明示あり ✅
- `StringUtil.isNullOrEmpty` で未入力チェック → s11の注意例に明示あり ✅
- `BeanValidationStrategy` をコンポーネント定義する → s16に明示あり ✅
- `@InjectForm` アノテーションを使う → s3に明示あり ✅
- バリデーション実行順序が保証されない → s11に明示あり ✅

verify_result = PASS

---

**結論**: ウェブアプリケーションでの相関バリデーション（メールアドレスの一致チェック）は、FormクラスにJakarta Bean Validationの `@AssertTrue` アノテーションを付けたbooleanメソッドを定義することで実装します。

**根拠**:

Formクラスに以下のようにメソッドを追加します。

```java
public class SampleForm {
  private String mailAddress;

  private String confirmMailAddress;

  @AssertTrue(message = "{compareMailAddress}")
  public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
      // どちらかが未入力の場合は、相関バリデーションは実施しない。(バリデーションOKとする)
      return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
  }

  // getter、setter は省略
}
```

`message` プロパティには、エラーメッセージのキー（例: `{compareMailAddress}`）を指定します。

業務アクション側では、`@InjectForm` と `@OnError` を組み合わせて使用します。

```java
@InjectForm(form = SampleForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  SampleForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのformを使って業務処理を行う
}
```

コンポーネント設定ファイルに `BeanValidationStrategy` の定義が必要です。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序は保証されないため、項目単体のバリデーション前に相関バリデーションが呼ばれる場合があります。任意項目の場合は、未入力チェック（`StringUtil.isNullOrEmpty`）を先に行い、どちらかが未入力なら `true` を返すようにしてください。
- データベースを使った相関バリデーション（例: メールアドレスの重複チェック）は、SQLインジェクション防止の観点から、`@AssertTrue` ではなく業務アクション内でバリデーション済みの値を使って実装してください。

参照: libraries-bean-validation.json:s11, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3

---