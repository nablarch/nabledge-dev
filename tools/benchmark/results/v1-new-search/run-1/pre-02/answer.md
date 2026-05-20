**結論**: ウェブアプリケーションの入力チェックは `@InjectForm` インターセプタを業務アクションのメソッドに設定し、Bean Validation のアノテーションを Form クラスのプロパティに定義することで実装します。

**根拠**:

**Step 1: コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Step 2: Form クラスを作成し、バリデーションアノテーションを設定する**

> **重要**: Formクラスのプロパティは必ず `String` 型で定義すること。String以外の型があると、不正な値送信時にBeanへの変換処理が失敗し予期せぬ例外が発生する。

```java
public class UserForm {

    @Domain("name")   // ドメインバリデーションを推奨
    @Required
    private String userName;

    @Domain("date")
    private String birthday;

    // getter、setter
}
```

アノテーションを個別指定する場合（ドメインバリデーションなし）:

```java
public class SampleForm {

    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    @Required
    private String userName;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    private String birthday;

    // getter、setter
}
```

**Step 3: 業務アクションに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション成功後、リクエストスコープからフォームを取得
    UserForm form = ctx.getRequestScopedVar("form");

    // 以降、業務処理
}
```

- `prefix`: リクエストパラメータのプレフィックス（`form.userId` のように HTML側でも合わせる）
- `validate`: バリデーショングループ名
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため必須

**Step 4: エラーメッセージをプロパティファイルに定義する**

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
```

**注意点**:
- `@OnError` は `@InjectForm` を付けたメソッドに必ず設定すること。
- 相関バリデーションは `@AssertTrue` アノテーションを使うが、バリデーション実行順は保証されないため、片方が未入力の場合でも例外が出ないようにロジックを組む必要がある。
- ドメインバリデーション（`@Domain`）の使用を推奨。個別アノテーション設定では実装ミスやメンテナンスコストが増大するため。

参照: component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-bean-validation.json:s9, component/libraries/libraries-bean-validation.json:s16, component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/libraries/libraries-bean-validation.json:s7