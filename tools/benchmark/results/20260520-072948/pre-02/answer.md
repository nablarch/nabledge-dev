**結論**: ウェブアプリケーションのフォームバリデーションは `@InjectForm` インターセプタを業務アクションのメソッドに付与することで実装する。入力値チェックには Bean Validation（`BeanValidationStrategy`）を使用し、フォームクラスのプロパティにアノテーションでバリデーションルールを設定する。

**根拠**:

**1. コンポーネント設定（BeanValidationStrategyの登録）**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. フォームクラスの作成**

プロパティは必ず `String` 型にする（型変換失敗による予期せぬ例外を防ぐため）。

```java
public class UserForm {

    @Required
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    private String userName;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    private String birthday;

    // getter、setter省略
}
```

**3. 業務アクションへの `@InjectForm` 設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

HTMLのinput要素のname属性は `form.xxx` の形式で指定する（`prefix = "form"` に対応）:

```html
<input name="form.userName" type="text" />
<input name="form.birthday" type="text" />
```

**注意点**:
- `@OnError` アノテーションが未設定の場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- フォームのプロパティは全て `String` 型にすること。数値型などに変換が必要な場合はバリデーション後に実施する
- データベースとの相関バリデーションは、SQLインジェクション等のリスクを避けるため業務アクション側で実装すること

参照: `component/libraries/libraries-bean-validation.json:s16`, `component/handlers/handlers-InjectForm.json:s1`, `component/handlers/handlers-InjectForm.json:s3`, `component/handlers/handlers-InjectForm.json:s4`, `component/libraries/libraries-bean-validation.json:s8`, `component/libraries/libraries-bean-validation.json:s6`