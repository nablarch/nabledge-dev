**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタと Bean Validation の組み合わせで実装します。コンポーネント設定に `BeanValidationStrategy` を登録し、業務アクションのメソッドに `@InjectForm` アノテーションを設定することで、リクエストパラメータのバリデーションが自動実行されます。

**根拠**:

**1. コンポーネント設定ファイルに BeanValidationStrategy を登録する**

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスを作成する**

Formクラスのプロパティは全て `String` 型として定義します（バリデーション前の変換失敗を防ぐため）。各プロパティにバリデーションアノテーションを設定します。

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

**3. ドメインバリデーション（推奨）**

個別にアノテーションを設定するより、ドメインBeanにルールをまとめるドメインバリデーションが推奨されます。

```java
// ドメインBeanの作成
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// DomainManager実装クラスの作成
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
  @Override
  public Class<SampleDomainBean> getDomainBean() {
      return SampleDomainBean.class;
  }
}
```

```xml
<!-- コンポーネント設定にdomainManagerという名前で登録 -->
<component name="domainManager" class="sample.SampleDomainManager"/>
```

Formクラスでは `@Domain` アノテーションで参照します。

```java
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

**4. 業務アクションへの @InjectForm 設定**

業務アクションのメソッドに `@InjectForm` と `@OnError` を設定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する。
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う。
}
```

`@InjectForm` により、`prefix` で指定したプレフィックス（この例では `form`）から始まるリクエストパラメータに対してバリデーションが実行されます。バリデーション成功後、フォームオブジェクトがリクエストスコープに格納されます。

**注意点**:
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため、必ず設定すること
- FormクラスのプロパティはすべてString型にすること（数値型などにすると変換処理で予期せぬ例外が発生する）
- 必須チェックの `@Required` はドメインBeanではなく個別のFormクラス側に設定すること

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