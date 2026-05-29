**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm`インターセプタとBean Validationを組み合わせて実装します。Formクラスにバリデーションアノテーションを定義し、アクションメソッドに`@InjectForm`を付与することで自動的にバリデーションが実行されます。

---

**根拠**:

**1. Formクラスの作成**

Formクラスのプロパティは**必ず全てString型**で定義します（型変換はバリデーション後に行うこと）。

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

// Formクラス
public class UserForm {
    @Domain("name")
    @Required            // @RequiredはドメインBean側ではなくForm側に設定すること
    private String userName;

    @Domain("date")
    private String birthday;
    // getter、setterは省略
}
```

直接アノテーションを設定する場合：

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

**2. アクションメソッドへのアノテーション設定**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // リクエストスコープからバリデーション済みのフォームを取得する
    UserForm form = ctx.getRequestScopedVar("form");
    // formを元に業務処理を行う
}
```

**3. コンポーネント設定ファイルへのBean Validationの設定**

```xml
<component name="validationStrategy"
    class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**4. エラーメッセージの画面表示（Thymeleafの例）**

バリデーションエラー時のメッセージはHTTPエラー制御ハンドラによってリクエストスコープに格納されます。

```html
<!-- 特定プロパティのエラーメッセージを表示 -->
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全メッセージを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**相関バリデーションが必要な場合**: `@AssertTrue`アノテーションを使用します。

```java
public class SampleForm {
    private String mailAddress;
    private String confirmMailAddress;

    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
        if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
            return true;  // どちらかが未入力の場合はバリデーションしない
        }
        return Objects.equals(mailAddress, confirmMailAddress);
    }
}
```

---

**注意点**:
- Formのプロパティは必ずString型にすること（String以外だと型変換失敗で障害になる）
- `@OnError`アノテーションを設定しない場合、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- 相関バリデーションはBean Validationの実行順序が保証されないため、未入力チェックをロジックに含める必要がある

---