**結論**: ウェブアプリケーションのバリデーションは、`@InjectForm` インターセプタを業務アクションのメソッドに設定することで実装します。Formクラスに Bean Validation のアノテーションを設定し、バリデーション済みフォームをリクエストスコープから取得して業務処理を行います。

**根拠**:

**1. BeanValidationStrategy の設定**

コンポーネント設定ファイルに `validationStrategy` という名前で `BeanValidationStrategy` を定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスの作成**

Formクラスのプロパティは必ず `String` 型で定義し、バリデーションアノテーションを設定します（ドメインバリデーションの使用を推奨）。

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

// Formクラス（@Domainでドメイン名を指定、@Requiredは個別のBeanに設定）
public class SampleForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;

    // getter、setter
}
```

**3. 業務アクションへの @InjectForm 設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // リクエストスコープからバリデーション済みのフォームを取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

- `prefix = "form"` を指定すると、`form.xxx` という名前のリクエストパラメータがバリデーション対象になります。
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いになるため、必ず設定してください。

**4. エラーメッセージの画面表示（Thymeleaf の例）**

バリデーションエラーメッセージはリクエストスコープの `ErrorMessages` から取得します。

```html
<!-- 特定項目のエラー表示 -->
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーの表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**5. エラーメッセージの定義**

プロパティファイルにメッセージIDをキーとしてメッセージを定義します。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formクラスのプロパティは全て `String` 型にすること。`String` 以外の型があると、不正な値が送信された際にバリデーション前にBean変換が失敗し障害になります。
- `@OnError` を必ず設定すること。設定しないとバリデーションエラーがシステムエラーになります。
- データベースとの相関バリデーションは、SQLインジェクション対策のため Bean Validation ではなく業務アクション側で実装してください。

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s6, libraries-bean-validation.json:s7, web-application-error-message.json:s1