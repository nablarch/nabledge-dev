**結論**: 入力チェック（バリデーション）エラー時のエラーメッセージをユーザーに返す方法は、アプリケーションの種類（Webアプリケーション / RESTfulウェブサービス）によって異なります。

## Webアプリケーションの場合

### 1. エラーメッセージの定義

バリデーションアノテーションに対応するメッセージをプロパティファイルで定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必ず入力してください。
```

### 2. バリデーション実行と遷移先の指定

アクションメソッドに `@InjectForm` と `@OnError` を設定します。バリデーションエラーが発生すると、`ApplicationException` がスローされ `@OnError` で指定した画面に遷移します。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理
}
```

> **注意**: `@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになります。

### 3. エラーメッセージの画面表示

HTTPエラー制御ハンドラが `ApplicationException` のメッセージを `ErrorMessages` に変換し、リクエストスコープの `errors` というキーで格納します。Thymeleafでの表示例:

**特定項目のエラーメッセージ**:
```html
<input type="text" name="form.userName" />
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

**全エラーメッセージの一覧表示**:
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 4. アクション内で特定項目にエラーを紐付けたい場合

DB重複チェックなどアクションハンドラ内でバリデーションを行う場合は `ValidationUtil#createMessageForProperty` を使用します。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

## RESTfulウェブサービスの場合

### 1. バリデーションの実行

リソースメソッドに `@Valid` アノテーションを設定します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 2. エラーレスポンスへのメッセージ設定

`ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを設定します。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        }
        return super.build(request, context, throwable);
    }

    private HttpResponse createResponseBody(ApplicationException ae) {
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        // エラーメッセージをJSONに変換してボディに設定
        return response;
    }
}
```

**注意点**:
- リクエストスコープのキー名はデフォルトで `errors`。コンポーネント設定で変更可能（`WebConfig#errorMessageRequestAttributeName`）
- JSPでもリクエストスコープのオブジェクトに直接アクセスしてエラー表示可能（カスタムタグ不使用でCSSフレームワークとの相性問題を回避できる）
- グローバルメッセージ（項目に紐付かないメッセージ）は `errors.globalMessages` で取得

参照: processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-HttpErrorHandler.json#s4, component/libraries/libraries-bean-validation.json#s7, component/libraries/libraries-bean-validation.json#s13, component/handlers/handlers-InjectForm.json#s3, component/handlers/handlers-InjectForm.json#s4, component/handlers/handlers-on-error.json#s3, component/handlers/handlers-jaxrs-response-handler.json#s7, component/handlers/handlers-jaxrs-bean-validation-handler.json#s4