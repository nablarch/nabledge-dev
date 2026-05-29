Step 5：回答生成に進みます。

**read_sections**: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s9`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`, `libraries-bean-validation.json:s6`, `libraries-bean-validation.json:s7`, `handlers-InjectForm.json:s4`, `libraries-bean-validation.json:s11`, `libraries-create-example.json:s2`

---

**Step 5: 回答生成**

ウェブアプリケーションの入力チェックは、**Bean Validation**（推奨）と `InjectForm` インターセプタを組み合わせて実装します。

---

**結論**: ウェブアプリケーションの入力チェックは、Formクラスにバリデーションアノテーションを付与し、業務アクションに `@InjectForm` を設定することで実装します。Bean Validation（Jakarta Bean Validation準拠）の使用が推奨されています。

**根拠**:

**① コンポーネント設定ファイルの準備**

Bean Validationを使用するには、`BeanValidationStrategy` を `validationStrategy` という名前で設定します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**② Formクラスの作成**

Formのプロパティは**全てString型**で定義し、アノテーションでバリデーションルールを設定します。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterは省略
}
```

（保守性を高めるため、ドメインバリデーション（`@Domain`）の使用を推奨。後述。）

**③ 業務アクションへの `@InjectForm` 設定**

`@InjectForm` で対象Formクラスとパラメータのプレフィックスを指定します。`@OnError` でバリデーションエラー時の遷移先を必ず設定してください。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

バリデーション成功後、バリデーション済みのFormオブジェクトがリクエストスコープに格納されます（デフォルトのキー名は `"form"`）。

**④ エラーメッセージの定義（プロパティファイル）**

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**⑤ ドメインバリデーション（推奨）**

バリデーションルールをドメイン単位で一元管理できます。

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}
// DomainManager実装 → コンポーネント定義に登録
// <component name="domainManager" class="sample.SampleDomainManager"/>

// 各Formでの使用
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになります
- String型以外のプロパティに不正値が送信されると変換処理が失敗し障害になります。**Formのプロパティは必ずString型**にしてください
- バリデーション実行順序は保証されないため、相関バリデーション（`@AssertTrue`）では項目単体の未入力を考慮した実装が必要です

参照: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s9`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s11`

---

**Step 6: verify**

Nablarch固有の主張を抽出して検証します。

| 主張 | 根拠セクション | 判定 |
|---|---|---|
| `BeanValidationStrategy` を `validationStrategy` という名前で設定 | `s16` | 支持 |
| `@InjectForm` アノテーションを業務アクションのメソッドに設定 | `s3` | 支持 |
| `InjectForm#prefix` でパラメータのプレフィックスを指定 | `s3` | 支持 |
| バリデーション済みFormがリクエストスコープに格納される | `s3` | 支持 |
| `@OnError` がないとバリデーションエラーがシステムエラー扱い | `s4` | 支持 |
| Formプロパティは全てString型 | `s8` | 支持 |
| ドメインBeanに `DomainManager` を実装し `domainManager` 名で登録 | `s9` | 支持 |
| 相関バリデーションは `@AssertTrue` を使用 | `s11` | 支持 |

`verify_result = PASS`

---

**Step 8: 回答出力**

---

**結論**: ウェブアプリケーションの入力チェックは、Formクラスにバリデーションアノテーション（Bean Validation）を付与し、業務アクションに `@InjectForm` インターセプタを設定することで実装します。

**根拠**:

**① コンポーネント設定（XML）**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**② Formクラスの作成**

プロパティは**全てString型**で定義し、アノテーションでバリデーションルールを指定します。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterは省略
}
```

**③ 業務アクションへの設定**

`@InjectForm` でFormクラスとパラメータのプレフィックスを指定し、`@OnError` でエラー時の遷移先を設定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // バリデーション済みのFormをリクエストスコープから取得
  UserForm form = ctx.getRequestScopedVar("form");

  // 業務処理...
}
```

**④ エラーメッセージの定義（プロパティファイル）**

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**⑤ ドメインバリデーション（推奨）**

バリデーションルールをドメイン単位で一元管理できます。個別にアノテーションを設定するより保守性が高いため推奨されます。

```java
// ドメインBean定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}
// DomainManager実装クラスを作成し、コンポーネント設定に登録
// <component name="domainManager" class="sample.SampleDomainManager"/>

// 各Formでの使用
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

**⑥ 相関バリデーション（複数項目）**

`@AssertTrue` アノテーションをBooleanメソッドに設定します。実行順序が保証されないため、未入力時の処理も考慮してください。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true; // 未入力の場合は相関バリデーションをスキップ
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

**注意点**:
- `@OnError` を必ず設定すること（未設定の場合、バリデーションエラーがシステムエラー扱いになる）
- Formのプロパティは**必ずString型**で定義すること（String以外の型だと変換失敗で障害になる）
- 相関バリデーションの実行順序は保証されないため、項目単体のバリデーション未実施を前提にロジックを実装すること

参照: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s9`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s11`

---