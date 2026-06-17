**結論**: ウェブアプリケーションでバリデーションエラーメッセージをユーザーに返すには、アクションメソッドに `@InjectForm` と `@OnError` を組み合わせて使用し、テンプレートエンジン側でリクエストスコープの `errors` オブジェクトからエラーメッセージを表示します。

**根拠**:

#### 1. バリデーションの設定

`BeanValidationStrategy` をコンポーネント設定ファイルに定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### 2. Formクラスにバリデーションルールを設定

```java
public class UserForm {
  @Required
  @Length(max = 10)
  private String userName;

  // getter、setterは省略
}
```

メッセージはプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

#### 3. アクションメソッドで `@InjectForm` と `@OnError` を設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  // バリデーション済みのフォームを取得
  UserForm form = ctx.getRequestScopedVar("form");
  // 業務処理...
}
```

`@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため必ず設定すること。

#### 4. エラーメッセージの表示 (Thymeleafの例)

バリデーションエラーが発生すると、`HTTPエラー制御ハンドラ` が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー名 `errors` に格納します。

特定のプロパティに対応したエラーメッセージを表示する場合:

```html
<input type='text' name='form.userName' />
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

全エラーメッセージをまとめて表示する場合:

```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- リクエストスコープのキー名はデフォルトで `errors`。変更したい場合は `WebConfig` の `errorMessageRequestAttributeName` で設定する。
- JSPを使う場合はカスタムタグ（`<n:errors>` 等）でも表示できるが、CSSフレームワークとの相性問題があるため、リクエストスコープのオブジェクトを直接参照する方法も選択できる。

参照: handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-HttpErrorHandler.json:s4, libraries-bean-validation.json:s16, libraries-bean-validation.json:s7, web-application-error-message.json