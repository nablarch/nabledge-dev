**結論**: ウェブアプリケーションのバリデーションは、FormクラスにBean Validationアノテーションを設定し、業務アクションメソッドに `@InjectForm` を付与することで実装します。

**根拠**:

### 1. コンポーネント設定（1回のみ）

コンポーネント設定ファイルに `BeanValidationStrategy` を登録します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスにバリデーションルールを設定

Formクラスのプロパティは**すべてString型**で宣言し、アノテーションを設定します。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterを定義
}
```

**ドメインバリデーション（推奨）**: バリデーションルールをドメイン単位で一元管理できます。

```java
// ドメインBeanの定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManagerの作成とコンポーネント登録
// <component name="domainManager" class="sample.SampleDomainManager"/>

// FormクラスでのDomainアノテーション使用
public class SampleForm {
  @Domain("name")
  @Required          // @RequiredはFormクラス側に設定
  private String userName;

  @Domain("date")
  private String birthday;
}
```

### 3. 業務アクションへの @InjectForm 設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

- `prefix`：バリデーション対象のリクエストパラメータのプレフィックス（例: `form.userId`）
- `@OnError` は必ず設定すること。設定しないとバリデーションエラーがシステムエラー扱いになります

### 4. エラーメッセージ定義

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formクラスのプロパティは必ずString型で宣言すること（型変換が必要な場合はバリデーション後に実施）
- `@InjectForm` に `@OnError` を必ず併用すること（未設定だとシステムエラー扱い）
- `@Required` アノテーションはドメインBeanではなく各Formクラス側に設定すること

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s7