**結論**: 入力チェックエラー時にエラーメッセージをユーザーに返すには、`@InjectForm` + `@OnError` の組み合わせを使います。バリデーションエラーが発生すると `ApplicationException` がスローされ、`@OnError` で指定したエラー画面に遷移します。

**根拠**:

### 基本パターン（ウェブアプリケーション）

**1. アクションクラスの実装**

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // バリデーション成功時のみここに到達する
    UserForm form = ctx.getRequestScopedVar("form");
    // 業務処理を行う
}
```

- `@InjectForm` でバリデーション対象のフォームクラスとプレフィックスを指定
- `@OnError` でバリデーションエラー時の遷移先を指定（**必須**。設定しないとシステムエラー扱いになる）

**2. コンポーネント設定（Bean Validationを使う場合）**

```xml
<component name="validationStrategy" 
           class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**3. エラーメッセージの定義（Bean Validation）**

```properties
# アノテーションのmessage属性で指定したメッセージIDに対応するメッセージを定義する
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

### 特定の項目に紐づくエラーメッセージを返したい場合

相関バリデーション等でアクション内でエラーが発生した場合、対象項目をエラーとしてハイライトするには `ValidationUtil#createMessageForProperty` を使用：

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

### メッセージに項目名を含めたい場合

```xml
<!-- コンポーネント設定ファイル -->
<component name="constraintViolationConverterFactory"
    class="nablarch.core.validation.ee.ItemNamedConstraintViolationConverterFactory" />
```

```properties
# メッセージ定義
nablarch.core.validation.ee.Required.message=入力してください。
# 項目名定義（完全修飾クラス名.プロパティ名）
sample.UserForm.name=ユーザ名
```
→ エラーメッセージ: `[ユーザ名]入力してください。`

**注意点**:
- `@OnError` を設定し忘れるとバリデーションエラーがシステムエラー扱いになるため必ず設定すること
- RESTful ウェブサービスの場合は `@Valid` アノテーションをリソースクラスのメソッドに設定する方式になる（詳細は `handlers-jaxrs-bean-validation-handler.json` 参照）
- バリデーションエラー時にもリクエストパラメータをJSPで参照したい場合は、`BeanValidationStrategy` の `copyBeanToRequestScopeOnError` プロパティを `true` に設定する

参照: `component/libraries/libraries-bean-validation.json#s7`, `component/libraries/libraries-bean-validation.json#s13`, `component/libraries/libraries-bean-validation.json#s16`, `component/libraries/libraries-bean-validation.json#s18`, `component/libraries/libraries-bean-validation.json#s19`, `component/handlers/handlers-InjectForm.json#s3`, `component/handlers/handlers-InjectForm.json#s4`