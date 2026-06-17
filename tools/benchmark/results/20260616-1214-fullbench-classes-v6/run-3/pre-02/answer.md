**結論**: ウェブアプリケーションのバリデーションは `@InjectForm` インターセプタを業務アクションメソッドに設定することで実装する。Formクラスにバリデーションアノテーションを定義し、`@OnError` でエラー時の遷移先を指定する。

---

**根拠**:

**1. コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスを作成する（プロパティは全て `String` 型）**

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

ドメインバリデーションを使うと、バリデーションルールの変更が容易になるため推奨:

```java
// ドメインBeanにルールを集中定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// 各FormではDomainアノテーションで参照する
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;

  // getter、setterは省略
}
```

**3. 業務アクションに `@InjectForm` と `@OnError` を設定する**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

---

**注意点**:
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること
- Formのプロパティは必ず `String` 型にすること。`String` 以外の型があると、不正な値が送信された際に変換処理が失敗して障害になる
- データベースとの相関バリデーション（重複チェックなど）は、SQL インジェクション等を防ぐため業務アクション側で実装すること

参照: component/libraries/libraries-bean-validation.json:s6, s7, s8, s9, s16 / component/handlers/handlers-InjectForm.json:s3, s4