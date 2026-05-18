**結論**: 入力チェックエラー時にユーザーへエラーメッセージを返す方法は、アプリケーション種別（ウェブアプリケーション / RESTfulウェブサービス）によって異なります。

## ウェブアプリケーションの場合

### 1. バリデーションの実行（`@InjectForm` インターセプタ）

業務アクションのメソッドに `@InjectForm` アノテーションを付けることで、リクエストパラメータに対してバリデーションが自動実行されます。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理...
}
```

### 2. エラー時の遷移先指定（`@OnError` アノテーション）

`@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになります。遷移先JSPを必ず指定してください。

### 3. エラーメッセージの画面表示

バリデーションエラーが発生すると、`HttpErrorHandler` が `ApplicationException` のメッセージ情報を `ErrorMessages` に変換し、リクエストスコープのキー `errors` に設定します。

```html
<!-- 特定項目のエラーメッセージ -->
<span th:if="${errors.hasError('form.userName')}"
      th:text="${errors.getMessage('form.userName')}"></span>

<!-- 全エラーメッセージ一覧 -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}"></li>
</ul>
```

### 4. エラーメッセージの定義

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

```java
public class SampleForm {
    @Length(max = 10)
    @Required
    private String userName;
}
```

## RESTfulウェブサービスの場合

### 1. バリデーションの実行（`@Valid` アノテーション）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

バリデーションエラーが発生すると `ApplicationException` が送出されます。

### 2. エラーレスポンスにメッセージを設定する

`JaxRsResponseHandler` の `errorResponseBuilder` をカスタマイズすることで、JSON形式でエラーメッセージをレスポンスボディに設定できます。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        }
        return super.build(request, context, throwable);
    }
}
```

**注意点**:

1. **`@OnError` を必ず設定する**: ウェブアプリでは `@InjectForm` を使う場合に `@OnError` がないとバリデーションエラーがシステムエラー扱いになります。
2. **Formのプロパティは全て `String` 型にする**: 型変換前にバリデーションを行うため、`String` 以外の型にすると変換処理が失敗します。
3. **エラーメッセージのリクエストスコープキー名**: デフォルトは `errors`。変更する場合は `WebConfig` の `errorMessageRequestAttributeName` プロパティで設定します。
4. **特定項目に紐づくエラーメッセージの手動生成**: DB相関バリデーション後にエラーを返したい場合は `ValidationUtil#createMessageForProperty` を使用します。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

参照: `libraries-bean-validation.json#s16`, `libraries-bean-validation.json#s7`, `handlers-InjectForm.json#s3`, `handlers-InjectForm.json#s4`, `handlers-HttpErrorHandler.json#s4`, `handlers-jaxrs-bean-validation-handler.json#s4`, `handlers-jaxrs-response-handler.json#s7`, `libraries-bean-validation.json#s13`