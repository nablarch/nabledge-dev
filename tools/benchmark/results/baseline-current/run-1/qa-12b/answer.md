**結論**: 入力チェックエラー時のメッセージ返却方法は、アプリケーション種別（ウェブアプリ・RESTful）によって異なります。

**根拠**:

### ウェブアプリケーションの場合

**1. バリデーション実行（InjectFormインターセプタ）**

`InjectForm` インターセプタを使って入力値チェックを行います。Bean Validationを使うには `BeanValidationStrategy` をコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. エラー時の遷移先を指定（OnErrorアノテーション）**

バリデーションエラー発生時の遷移先画面は `@OnError` アノテーションで指定します。`@OnError` がないとバリデーションエラーがシステムエラー扱いになるため必須です。

**3. エラーメッセージの定義**

`NablarchMessageInterpolator` がデフォルトで使われ、メッセージ管理機能でメッセージを定義します。

```java
public class SampleForm {
  @Length(max = 10)
  @Required
  private String userName;
}
```

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**4. 特定項目に紐づくエラーをプログラムで生成する場合**

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

### RESTfulウェブサービスの場合

**1. バリデーション実行**

リソースクラスのメソッドに `@Valid` アノテーションを設定します。

**2. エラーレスポンスにメッセージを設定する**

`ErrorResponseBuilder` を継承したクラスを作成し、`ApplicationException` が発生した際にJSONなどの形式でメッセージをレスポンスに含めます。

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
        HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        response.write(objectMapper.writeValueAsString(errorMessages));
        return response;
    }
}
```

**注意点**:
- `@OnError` アノテーションは必ず設定すること。未設定の場合、バリデーションエラーがシステムエラー扱いになります。
- `BeanValidationStrategy` のエラーメッセージソート順はアプリケーションサーバ実装依存です。プロジェクト固有のソート順が必要な場合は `BeanValidationStrategy` を継承して対応してください。
- メッセージにフィールド名を含めたい場合は `ItemNamedConstraintViolationConverterFactory` を使うと `[ユーザ名]入力してください。` のような形式になります。

参照:
- component/libraries/libraries-bean-validation.json#s7
- component/libraries/libraries-bean-validation.json#s13
- component/libraries/libraries-bean-validation.json#s16
- component/libraries/libraries-bean-validation.json#s19
- component/handlers/handlers-InjectForm.json#s4
- component/handlers/handlers-jaxrs-response-handler.json#s7