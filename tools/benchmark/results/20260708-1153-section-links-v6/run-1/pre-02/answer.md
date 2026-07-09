**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタと Bean Validation を組み合わせて実装します。コンポーネント設定に `BeanValidationStrategy` を定義し、業務アクションに `@InjectForm` と `@OnError` アノテーションを設定することで、フォームの入力値が自動的にバリデーションされます。

**根拠**:

**1. コンポーネント設定ファイルへの設定**

Bean Validation を `InjectForm` インターセプタで使用するには、`BeanValidationStrategy` を `validationStrategy` という名前で登録します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスへのバリデーションルール設定**

Formクラスのプロパティは **すべて String 型** で定義し、アノテーションを付与します。

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

メンテナンスコスト削減のため、**ドメインバリデーション**の使用を推奨します。

```java
// ドメインBean（バリデーションルールを集約定義）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// コンポーネント設定ファイルに登録
// <component name="domainManager" class="sample.SampleDomainManager"/>

// FormクラスはDomainを参照するだけ（@Required は個別のBean側に設定）
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;

  @Domain("date")
  private String birthday;
}
```

**3. 業務アクションへの実装**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // form を元に業務処理を行う
}
```

**4. エラーメッセージの定義**

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formクラスのプロパティは **必ず String 型** にすること。String 以外の型のプロパティに不正値が送信されると、バリデーション前に変換処理が失敗し障害になる。
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになるため注意。
- データベースとの相関バリデーションは、SQLインジェクション防止のため Bean Validation ではなく業務アクション側で実装すること。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションルールの設定方法
  ドメインバリデーションを使う
  ウェブアプリケーションのユーザ入力値のチェックを行う
  Bean Validationを使うための設定
  バリデーションエラー時のエラーメッセージを定義する
- InjectForm インターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md
  InjectFormを使用する
  バリデーションエラー時の遷移先を指定する