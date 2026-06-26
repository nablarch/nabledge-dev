**結論**: ウェブアプリケーションでの入力チェック（バリデーション）は、`@InjectForm` アノテーション（InjectFormインターセプタ）を業務アクションのメソッドに設定することで実装します。Bean Validationを使用する場合は、コンポーネント設定ファイルへの `BeanValidationStrategy` の登録が必要です。

---

**根拠**:

**① 依存モジュールの追加**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>

<!-- Bean Validationを使用する場合 -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-validation-ee</artifactId>
</dependency>
```

**② コンポーネント設定ファイルに BeanValidationStrategy を登録**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**③ Formクラスに Bean Validation アノテーションを設定**

```java
public class UserForm {
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

**④ 業務アクションに `@InjectForm` と `@OnError` を設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する。
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う。
}
```

- `prefix = "form"` を指定すると、`form.userId` のようにプレフィックスが付いたリクエストパラメータがバリデーション対象になります。
- バリデーション成功時は、リクエストスコープにバリデーション済みフォームが格納されます。

**⑤ バリデーションエラー時のメッセージ定義**

デフォルトでは[メッセージ管理](../../component/libraries/libraries-message.json)を使用してエラーメッセージを構築します。アノテーションの `message` 属性にメッセージIDを `{...}` 形式で指定し、プロパティファイルにメッセージを定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

---

**注意点**:
- `@OnError` を設定していない場合、バリデーションエラーがシステムエラー扱いになるため、必ず設定すること。
- Bean Validationのグループを使い分けたい場合は、`@InjectForm` の `validationGroup` 属性にグループクラスを指定できます（例: `validationGroup = Create.class`）。

参照: `libraries-bean-validation.json:s6`, `libraries-bean-validation.json:s7`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s2`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `handlers-InjectForm.json:s5`