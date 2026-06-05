必要なセクションが揃いました。回答を生成します。

---

**結論**: ウェブアプリケーションの入力バリデーションは、`@InjectForm`インターセプタとBean Validationを組み合わせて実装する。Formクラスのプロパティにバリデーションアノテーションを設定し、業務アクションのメソッドに`@InjectForm`アノテーションを付与する。

---

**根拠**:

### 1. コンポーネント設定（XML）

Bean Validationを`@InjectForm`インターセプタで使用するために、`BeanValidationStrategy`を`validationStrategy`という名前でコンポーネント定義する：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスの実装

Formクラスのプロパティは**全て`String`型**で定義し、バリデーションアノテーションを付与する：

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

ドメインごとにルールを集中管理したい場合は、ドメインBeanと`@Domain`アノテーションを使うドメインバリデーション（推奨）を使用できる：

```java
// ドメインBean（ルール定義）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// フォームクラス（ドメイン名を指定）
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

### 3. 業務アクションの実装

業務アクションのメソッドに`@InjectForm`と`@OnError`を設定する：

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

---

**注意点**:
- Formクラスのプロパティは必ず`String`型にすること。`String`以外の型があると、バリデーション実施前の型変換が失敗して予期せぬ例外が発生する
- `@OnError`アノテーションが設定されていない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- データベースとの相関バリデーションはBean Validationでは行わず、バリデーション実行後の業務アクション側で実装すること（バリデーション前の安全でない値でDBアクセスするとSQLインジェクション等の脆弱性の原因になる）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s9, libraries-bean-validation.json:s6

---