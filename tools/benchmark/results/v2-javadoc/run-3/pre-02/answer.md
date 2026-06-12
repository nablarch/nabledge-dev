必要なセクションを特定しました。`read-sections.sh`に渡すセクションを決定して回答を生成します。

**read_sections**: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s16`, `libraries-bean-validation.json:s6`, `libraries-bean-validation.json:s9`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `web-application-feature-details.json:s2`

---

**結論**: ウェブアプリケーションの入力チェックは、**Bean Validation** のアノテーションを設定した Form クラスと、**`@InjectForm` インターセプタ**を組み合わせて実装します。

---

**根拠**:

### 1. コンポーネント設定ファイルに BeanValidationStrategy を定義する

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Form クラスを作成してバリデーションルールを設定する

アノテーションを Field または getter に設定します。**プロパティの型は必ず `String` で定義**してください。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setter は省略
}
```

> **推奨**: 個別アノテーションの設定は実装ミスが増えるため、**ドメインバリデーション（`@Domain`）の使用を推奨**します。

```java
// ドメイン定義 Bean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// Form 側は @Domain でドメイン名を指定するだけ
public class SampleForm {
  @Domain("name")
  @Required  // 必須かどうかは Form 側で設定する
  private String userName;
}
```

### 3. アクションメソッドに `@InjectForm` と `@OnError` を設定する

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // form を元に業務処理を行う
}
```

- `form`: バリデーション対象の Form クラスを指定
- `prefix`: リクエストパラメータのプレフィックス（例: `form.userId` の `form` 部分）
- `validate`: バリデーションメソッド名（グループ名）

バリデーション成功後、リクエストスコープに `form` というキーでバリデーション済みオブジェクトが格納されます。

---

**注意点**:
- **Formのプロパティは全て `String` 型で定義**すること。`String` 以外の型があると、不正な値が入力された際に変換処理が失敗して予期せぬ例外が発生します
- **`@OnError` を必ず設定**すること。設定がない場合、バリデーションエラーがシステムエラー扱いになります
- データベースとの相関バリデーション（重複チェック等）は、SQLインジェクション等のリスクを避けるため、Bean Validation ではなく業務アクション側で行うこと

---

参照: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s16`, `libraries-bean-validation.json:s6`, `libraries-bean-validation.json:s9`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`

---