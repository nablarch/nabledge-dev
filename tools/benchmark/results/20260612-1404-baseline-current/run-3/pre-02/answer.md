**結論**: ウェブアプリケーションのバリデーションは、業務アクションメソッドに `@InjectForm` アノテーションを付与し、FormクラスのプロパティにBean Validationアノテーションを設定することで実装する。

**根拠**:

**① Formクラスの作成**

Formクラスのプロパティは**すべてString型**で定義し、バリデーションアノテーションを設定する。

```java
public class UserForm {

  @Domain("name")   // ドメインバリデーション推奨
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setter は省略
}
```

ドメインバリデーションを使う場合は、ドメインごとのルールを持つドメインBeanと `DomainManager` 実装クラスを作成し、コンポーネント設定ファイルに登録する。

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**② 業務アクションへの設定**

`@InjectForm` と `@OnError` をアクションメソッドに設定する。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // バリデーション済みフォームの取得
  UserForm form = ctx.getRequestScopedVar("form");

  // form を元に業務処理を行う
}
```

**③ Bean Validationをウェブで使うためのコンポーネント設定**

```xml
<component name="validationStrategy"
    class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**④ エラーメッセージの定義**

デフォルトではメッセージ管理機能（プロパティファイル）を使用する。アノテーションのデフォルトメッセージIDをキーにメッセージを定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、**必ず設定すること**
- Formクラスのプロパティは**すべてString型**にすること。型変換が必要な場合はバリデーション後に実施する
- `@Required` はドメインBeanではなく、個別のFormクラス側に設定すること
- 相関バリデーションが必要な場合は `@AssertTrue` アノテーションをgetterメソッドに設定する（バリデーション実行順序は保証されないため、未入力時の例外対策が必要）

参照: `component/handlers/handlers-InjectForm.json:s3`, `component/handlers/handlers-InjectForm.json:s4`, `component/libraries/libraries-bean-validation.json:s8`, `component/libraries/libraries-bean-validation.json:s9`, `component/libraries/libraries-bean-validation.json:s16`, `component/libraries/libraries-bean-validation.json:s7`