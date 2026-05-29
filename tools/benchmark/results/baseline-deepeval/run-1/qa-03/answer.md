必要なセクションが揃いました。セクション選択をまとめます。

**Step 3: セクション選択まとめ**

**selected_pages:**
1. `component/libraries/libraries-bean-validation.json` — 相関バリデーションの実装方法（s11）を直接カバー
2. `component/handlers/handlers-InjectForm.json` — ウェブアプリのバリデーション実行方法をカバー
3. `component/libraries/libraries-nablarch-validation.json` — 相関バリデーション(s14)があるが、Bean Validationが優先されるためsecondary
4. `processing-pattern/web-application/web-application-feature-details.json` — 入力値チェックの概要のみ、Bean ValidationとInjectFormに情報が集約されているためskip

**selected_sections:**
- `libraries-bean-validation.json:s11` → **high** （相関バリデーションの実装例がそのまま回答になる）
- `handlers-InjectForm.json:s3` → **partial** （ウェブアプリでの実行方法の背景情報）
- `libraries-bean-validation.json:s16` → **partial** （ウェブアプリ設定の補足）

**Step 4: セクション読み込み**
既にs11、s3、s16の内容を読み込んでいます。

`read_sections`: `libraries-bean-validation.json:s11`, `handlers-InjectForm.json:s3`, `libraries-bean-validation.json:s16`

**Step 5: 回答生成**

s11の内容から回答を生成します。

`answer_text`:

---

**結論**: Formクラスに `@AssertTrue` アノテーションを付けたgetter（boolean型）を定義し、その中で2項目の値を比較する。

**根拠**:

Jakarta Bean Validationの `@AssertTrue` アノテーションを使います。

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

バリデーションエラー時のメッセージIDは `message` 属性に指定します（`{compareMailAddress}` のようにメッセージプロパティファイルのキーを `{}` で囲む）。

**注意点**:
- Jakarta Bean Validationではバリデーションの実行順序が保証されないため、単項目バリデーションより前に相関バリデーションが呼ばれる可能性がある
- いずれかの項目が未入力（任意項目）の場合、`null` が渡されても例外が発生しないよう実装すること:

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

- ウェブアプリケーションでBean Validationを使うには、コンポーネント定義に `BeanValidationStrategy` を設定する必要がある:

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

- 業務アクションには `@InjectForm` インターセプタを付けてバリデーションを実行する

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`

---

**Step 6: 検証**

Nablarch固有のクレームを確認：
- `@AssertTrue` アノテーション → Jakarta Bean Validation標準仕様（s11に明示）✅
- `Objects.equals(mailAddress, confirmMailAddress)` → s11のコード例そのまま ✅
- `StringUtil.isNullOrEmpty` → s11のコードに明記 ✅
- `BeanValidationStrategy` → s16に明示 ✅
- `@InjectForm` → s3に明示 ✅

`verify_result = PASS`

**Step 7:** `final_answer = answer_text`

---

**結論**: Formクラスに `@AssertTrue` アノテーションを付けたboolean型のgetterを定義し、その中でメールアドレスと確認用メールアドレスを比較することで相関バリデーションを実装できます。

**根拠**:

Jakarta Bean Validationの `@AssertTrue` アノテーションを使います。

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

バリデーションエラー時のメッセージは `message` 属性にメッセージIDを `{}` で囲んで指定します。

**注意点**:

1. **実行順序の非保証**: Jakarta Bean Validationでは単項目バリデーションより前に相関バリデーションが呼ばれる場合がある。そのため、いずれかの項目が未入力（任意項目）の場合は例外が発生しないよう対応が必要:

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

2. **ウェブアプリの設定**: Bean Validationを使用するにはコンポーネント定義に以下を追加:

   ```xml
   <component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
   ```

3. **業務アクション**: `@InjectForm` アノテーションでバリデーションを実行し、エラー時の遷移先は `@OnError` で指定:

   ```java
   @InjectForm(form = SampleForm.class, prefix = "form")
   @OnError(type = ApplicationException.class, path = "forward://input.jsp")
   public HttpResponse handle(HttpRequest req, ExecutionContext ctx) { ... }
   ```

参照: `libraries-bean-validation.json:s11`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`

---