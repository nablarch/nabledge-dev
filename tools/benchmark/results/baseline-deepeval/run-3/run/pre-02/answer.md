**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタと Bean Validation（アノテーション）を組み合わせて実装します。フォームクラスに `@Required` / `@Length` 等のアノテーションを付け、業務アクションに `@InjectForm` と `@OnError` を設定することで、バリデーション実行・エラー遷移が自動的に行われます。

---

**根拠**:

**① コンポーネント設定ファイルへの設定**

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

ドメインバリデーションを使う場合は、あわせて `DomainManager` 実装クラスも定義します。

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**② フォームクラスの作成**

フォームクラスのプロパティは**全て `String` 型**にすること（型変換エラーを防ぐため）。
アノテーションは Field か getter に設定します（setter には設定不可）。

```java
public class SampleForm {

  @Domain("name")
  @Required
  private String userName;

  @Domain("date")
  private String birthday;

  // getter、setterは省略
}
```

ドメインバリデーションを使う場合は、ドメインBeanでルールを一元管理できます。

```java
public class SampleDomainBean {

    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}
```

**③ 業務アクションへの設定**

`@InjectForm` を業務アクションのリクエスト処理メソッドに設定します。
`@OnError` を必ず設定してください（設定がないとバリデーションエラーがシステムエラー扱いになります）。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する。
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う。
}
```

HTMLのinput要素は `form.` プレフィックスで定義します。

```html
<!-- バリデーション対象外 -->
<input name="flag" type="hidden" />

<!-- バリデーション対象 -->
<input name="form.userId" type="text" />
<input name="form.password" type="password" />
```

**④ エラーメッセージの表示（Thymeleaf）**

バリデーションエラーのメッセージは `ErrorMessages` オブジェクトとしてリクエストスコープに格納されます。

```html
<!-- 特定プロパティのエラーを表示 -->
<input type='text' name='form.txt' />
<span class="error" th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーを表示 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**⑤ エラーメッセージの定義（.properties）**

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必ず入力してください。
```

**⑥ 相関バリデーション**

複数項目の相関チェックは `@AssertTrue` アノテーションを getter に付けます。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true; // どちらかが未入力の場合はスキップ
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

---

**注意点**:
- フォームクラスのプロパティは必ず `String` 型にすること。`int` 等にすると不正入力で変換例外が発生します。
- `@OnError` の設定を忘れると、バリデーションエラーがシステムエラー扱いになります。
- `@Required` はドメインBean側でなく、個別の Form クラス側に設定すること（必須かどうかは機能設計による）。
- Bean Validationではバリデーション実行順序が保証されないため、相関バリデーションは単体バリデーション未実施の状態でも例外が起きないよう実装すること。

参照: component/libraries/libraries-bean-validation.json:s16, component/handlers/handlers-InjectForm.json:s3, component/handlers/handlers-InjectForm.json:s4, component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-bean-validation.json:s9, component/libraries/libraries-bean-validation.json:s7, processing-pattern/web-application/web-application-error-message.json:s1, component/libraries/libraries-bean-validation.json:s11

---