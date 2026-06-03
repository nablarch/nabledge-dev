Step 4のread-sections.shが完了しました。取得したセクション内容をもとにStep 5で回答を生成し、Step 6でベリファイします。

**結論**: ウェブアプリケーションでのバリデーションは `@InjectForm` インターセプタを業務アクションメソッドに設定し、Formクラスのプロパティに Bean Validation アノテーション（`@Required`、`@Length`、`@SystemChar` など）を付与することで実装します。

**根拠**:

**1. Formクラスの作成（プロパティは必ず `String` 型）**

```java
public class UserForm {

  @Required
  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setter
}
```

**2. コンポーネント設定ファイルに `BeanValidationStrategy` を定義**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**3. 業務アクションに `@InjectForm` を設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://inputForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // バリデーション済みのフォームをリクエストスコープから取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // 業務処理...
}
```

**4. ドメインバリデーション（推奨）**

個別にアノテーションを設定するよりも、ドメインBeanでバリデーションルールを集約することが推奨されます。

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

コンポーネント設定：
```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

各Formで `@Domain` アノテーションを使用：
```java
public class UserForm {
  @Domain("name")
  @Required   // 必須はドメインBeanではなく個別Beanに設定
  private String userName;
}
```

**5. エラーメッセージの定義（プロパティファイル）**

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formクラスのプロパティは**必ず `String` 型**にすること。`String` 以外の型を使用すると、不正な値が送信された際にバリデーション前に変換処理が失敗し、予期せぬ例外が発生します。
- `@OnError` アノテーションを `@InjectForm` と一緒に設定しないと、バリデーションエラーがシステムエラー扱いになります。
- バリデーション実行順序はJakarta Bean Validationでは保証されないため、相関バリデーションでは項目単体のバリデーション未実施の場合を考慮した実装が必要です。

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s9, libraries-bean-validation.json:s7

---