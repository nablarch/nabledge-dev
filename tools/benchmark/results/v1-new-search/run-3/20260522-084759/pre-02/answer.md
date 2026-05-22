必要なセクション情報が揃いました。Step 4のread_sectionsとStep 5の回答生成に進みます。

**read_sections:**
- `component/libraries/libraries-bean-validation.json:s6`
- `component/libraries/libraries-bean-validation.json:s8`
- `component/libraries/libraries-bean-validation.json:s9`
- `component/libraries/libraries-bean-validation.json:s16`
- `component/handlers/handlers-InjectForm.json:s3`
- `component/handlers/handlers-InjectForm.json:s4`
- `processing-pattern/web-application/web-application-error-message.json`（セクションなし、本文のみ）

Step 6のverify後、回答を出力します。

---

**結論**: ウェブアプリケーションのバリデーションは `@InjectForm` インターセプタを業務アクションメソッドに付与することで実装する。Nablarchでは Bean Validation（Jakarta EE準拠）の使用を推奨している。

---

**根拠**:

#### 1. コンポーネント設定ファイルに BeanValidationStrategy を登録する

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### 2. Formクラスを作成する（全プロパティは `String` 型で定義）

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

ドメインバリデーション（推奨）を使う場合は、ドメインBeanにルールをまとめて `@Domain` で参照する:

```java
// ドメインBean（ルールをまとめる）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// Formクラスはドメイン名のみ指定
public class UserForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;
}
```

ドメインBeanを有効化するには `DomainManager` 実装クラスをコンポーネント定義に登録:

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

#### 3. 業務アクションメソッドに `@InjectForm` と `@OnError` を設定する

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みのフォームをリクエストスコープから取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

- `prefix` には画面フォームのinput name属性のプレフィックスを指定（例: `name="form.userId"`）
- バリデーション成功時、フォームオブジェクトがリクエストスコープに格納される

#### 4. エラーメッセージを画面に表示する（Thymeleaf例）

```html
<!-- 特定プロパティのエラー表示 -->
<input type="text" name="form.userName" />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーメッセージの一覧表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

---

**注意点**:
- Formのプロパティは**必ず `String` 型**で定義すること。String以外の型があると、不正値送信時にBeanへの変換処理が失敗して障害になる。
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため、必ず設定すること。
- データベースとの相関バリデーション（重複チェックなど）は、SQLインジェクション防止のためBean Validationではなく業務アクション側で実装すること。

参照: `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s9`, `libraries-bean-validation.json:s16`, `handlers-InjectForm.json:s3`, `handlers-InjectForm.json:s4`, `web-application-error-message.json`

---