**結論:** ウェブアプリケーションの入力バリデーションは、業務アクションのメソッドに `@InjectForm` アノテーションを付与し、FormクラスのフィールドにBean Validationアノテーション（`@Required`、`@Length`、`@SystemChar` など）を設定することで実現します。

---

**根拠:**

**1. コンポーネント設定ファイルにBeanValidationStrategyを登録する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

コンポーネント名は必ず `validationStrategy` とすること。

---

**2. Formクラスにバリデーションルールを定義する**

フィールドの型は**必ずすべてString**にすること（String以外の型があると変換失敗で例外になる）。

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

ドメインバリデーションを使う場合（推奨）：

```java
// ドメインBeanの定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManagerの実装（コンポーネント名はdomainManager）
// コンポーネント設定ファイル:
// <component name="domainManager" class="sample.SampleDomainManager"/>

// FormクラスはDomainアノテーションでドメイン名を指定する
public class UserForm {
  @Domain("name")
  @Required          // @RequiredはドメインBeanではなくForm側に設定する
  private String userName;

  @Domain("date")
  private String birthday;
}
```

---

**3. 業務アクションに@InjectFormを付与する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを使って業務処理を実行する
}
```

- `prefix` には、HTMLフォームの入力項目のname属性プレフィックス（`form.userName` なら `form`）を指定する
- `@OnError` でバリデーションエラー時の遷移先を必ず指定すること。指定しないとバリデーションエラーがシステムエラー扱いになる

---

**4. HTMLでバリデーション対象項目を定義する**

```html
<!-- バリデーション対象: prefixに合わせてname属性を設定 -->
<input name="form.userName" type="text" />
<input name="form.birthday" type="text" />
```

---

**注意点:**

- FormクラスのプロパティはすべてStringで定義すること。JavaScriptを無効化された場合でもサーバサイドバリデーションは必ず通る必要がある
- `@OnError` を省略するとバリデーションエラーがシステムエラーになる
- `@Required` アノテーションはドメインBeanではなく、各FormクラスのField側に設定すること（必須かどうかは機能設計による）

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  ウェブアプリケーションのユーザ入力値のチェックを行う
  バリデーションルールの設定方法
  ドメインバリデーションを使う
- InjectForm インターセプタ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-InjectForm.md
  InjectFormを使用する
  バリデーションエラー時の遷移先を指定する
- バリデーションエラーのメッセージを画面表示する
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-error-message.md