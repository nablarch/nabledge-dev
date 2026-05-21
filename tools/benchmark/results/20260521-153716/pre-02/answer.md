セクション内容を確認できました。Step 5の回答を生成します（verify含む）。

---

**結論**: ウェブアプリケーションの入力チェックは、業務アクションのメソッドに `@InjectForm` アノテーションを設定することで実現する。Bean Validationを使う場合は、コンポーネント設定ファイルに `BeanValidationStrategy` を登録し、フォームクラスにバリデーションアノテーションを定義する。

---

**根拠**:

### 1. コンポーネント設定ファイルへの登録（Bean Validation使用時）

```xml
<!-- BeanValidationStrategyをvalidationStrategyという名前で登録する -->
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. フォームクラスの定義

フォームクラスのプロパティは**全てString型**で定義すること（他の型だと変換失敗で予期せぬ例外が発生する）。バリデーションルールはドメインバリデーションの使用を推奨。

```java
// ドメインBeanでルールを一元管理（推奨）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// フォームクラスは@Domainでドメイン名を指定
public class UserForm {
    @Domain("name")
    @Required            // 必須かどうかはドメインBeanではなくフォーム側に設定
    private String userName;

    @Domain("date")
    private String birthday;

    // getter、setter省略
}
```

### 3. 業務アクションへの設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション成功後、リクエストスコープからフォームを取得できる
    UserForm form = ctx.getRequestScopedVar("form");

    // formをもとに業務処理を行う
}
```

### 4. エラーメッセージの定義

```properties
# アノテーションのデフォルトメッセージIDをキーに定義する
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

---

**注意点**:
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになるため必ず設定すること。
- データベースとの相関バリデーション（重複チェック等）は、SQLインジェクション脆弱性防止のためBean Validation内ではなく業務アクション側で実装すること。
- 複数項目の相関バリデーションは `@AssertTrue` を使い、未入力時のnull考慮を必ず実装すること。

参照: libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-on-error.json:s3, libraries-bean-validation.json:s6, libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s7, libraries-bean-validation.json:s11

---