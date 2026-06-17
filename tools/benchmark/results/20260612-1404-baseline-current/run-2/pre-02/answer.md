**結論**: ウェブアプリケーションのバリデーションは、①Formクラスへの Bean Validation アノテーション設定、②`BeanValidationStrategy` のコンポーネント登録、③業務アクションへの `@InjectForm` + `@OnError` の付与、の3ステップで実装する。

---

**根拠**:

**Step 1: FormクラスにバリデーションルールをアノテーションとAL定義**

Formクラスのプロパティはすべて `String` 型にすること（数値型などにすると、Beanへの変換処理がバリデーション前に失敗し障害となる）。

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

ドメインバリデーションを使うと、ルール定義を一元管理できて推奨:

```java
// ドメインBeanの作成
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// Formで@Domainを使う
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;

  @Domain("date")
  private String birthday;
}
```

**Step 2: コンポーネント設定ファイルに `BeanValidationStrategy` を登録**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Step 3: 業務アクションに `@InjectForm` と `@OnError` を設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する。
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う。
}
```

- `prefix = "form"` → `form.xxx` という名前のリクエストパラメータがバリデーション対象になる
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること

**バリデーションエラーのメッセージをエラーメッセージ定義する**

`ApplicationException` 発生時のメッセージはメッセージ管理（プロパティファイル）で定義する:

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須です。
```

**バリデーションエラーのメッセージ表示（Thymeleaf）**

```html
<!-- 特定プロパティのエラーを表示 -->
<span th:if="${errors.hasError('form.userName')}"
      th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全てのエラーメッセージを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- Formのプロパティはすべて `String` 型にすること（バリデーション前の型変換失敗を防ぐため）
- `@OnError` を忘れると、バリデーションエラーがシステムエラーとして扱われる
- ドメインバリデーションの利用を推奨（個別アノテーション指定よりもメンテナンスコストが低い）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s7