**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` アノテーションと Bean Validation（アノテーション）を組み合わせて実装します。Formクラスのプロパティに `@Required`、`@Length`、`@SystemChar` 等のアノテーションを付与し、業務アクションに `@InjectForm` を付与することでバリデーションが自動実行されます。

**根拠**:

**1. Formクラスの作成（バリデーションルール定義）**

Formクラスのプロパティは**すべてString型**で定義し、アノテーションでルールを設定します。

```java
public class UserForm {

  @Required
  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  private String userName;

  @Required
  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setterは省略
}
```

**2. ドメインバリデーション（推奨）**

個別にアノテーションを設定するよりも、ドメインBeanにルールをまとめる方法を推奨します。

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManager実装クラス
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
    @Override
    public Class<SampleDomainBean> getDomainBean() {
        return SampleDomainBean.class;
    }
}
```

コンポーネント設定ファイル:
```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

ドメインを使うFormクラス:
```java
public class SampleForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;
}
```

**3. 業務アクションでの @InjectForm 使用**

`@InjectForm` アノテーションを業務アクションのメソッドに付与し、`@OnError` でエラー時の遷移先を指定します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みのフォームをリクエストスコープから取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

**4. コンポーネント設定（Bean Validationを有効化）**

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**5. エラーメッセージの定義**

プロパティファイルにアノテーションのメッセージIDをキーとして定義します。

```properties
nablarch.core.validation.ee.Required.message=必須項目です。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formクラスのプロパティは必ず `String` 型にすること。String以外だとBeanへの変換がバリデーション前に失敗し、予期せぬ例外が発生する。
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。
- `@Required` アノテーションはドメインBeanではなく個別のFormクラス側に設定すること（必須かどうかは機能設計によるため）。

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16, libraries-bean-validation.json:s6, libraries-bean-validation.json:s7, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4