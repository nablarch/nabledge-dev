**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタを業務アクションのメソッドに設定して行う。FormクラスのプロパティにBean Validationのアノテーションを設定し、バリデーション済みフォームをリクエストスコープ経由で取得する。

**根拠**:

**1. コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. バリデーションルールをFormクラスに定義する（プロパティは全てString型）**

```java
public class UserForm {

    @Required
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    private String userName;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    private String birthday;

    // getter、setterは省略
}
```

ドメインバリデーションを使う場合は、ドメインBeanと `DomainManager` 実装クラスを作成し、Formには `@Domain` アノテーションだけを設定する（推奨）:

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// DomainManager実装
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
    @Override
    public Class<SampleDomainBean> getDomainBean() {
        return SampleDomainBean.class;
    }
}
```

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**3. 業務アクションのメソッドに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

`prefix = "form"` を指定すると、`form.userId` など `form` から始まるリクエストパラメータがバリデーション対象となる。

**注意点**:
- Formクラスのプロパティは**必ず `String` 型**で定義すること。String以外の型に数値以外が送信されると変換処理が失敗し障害となる
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、必ず設定すること
- データベースとの相関バリデーションは、SQLインジェクション防止のため、Bean Validation内ではなく業務アクション側で実装すること

参照: component/libraries/libraries-bean-validation.json:s6, s8, s9, s16, component/handlers/handlers-InjectForm.json:s3, s4