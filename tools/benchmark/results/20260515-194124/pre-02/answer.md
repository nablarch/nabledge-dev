**結論**: NablarchのBean Validationを使用することが推奨です。Formクラスのフィールドにアノテーションでバリデーションルールを定義し、Webアプリケーションでは`@InjectForm`インターセプタ、RESTfulサービスでは`@Valid`アノテーションで実行します。

**根拠**:

### 1. Formクラスの定義（バリデーションルールの設定）

Formクラスのフィールド（すべて `String` 型）にアノテーションを設定します。

```java
public class SampleForm {

    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    @Required
    private String userName;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    private String birthday;

    // getter、setter省略
}
```

> **重要**: フィールドは必ず `String` 型にすること。`String` 以外の型だとバリデーション前のBean変換で例外が発生する可能性があります。

### 2. Webアプリケーションでの実装

**コンポーネント設定**（`BeanValidationStrategy`を登録）:
```xml
<component name="validationStrategy"
    class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**業務アクションへの`@InjectForm`設定**:
```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");

    // 業務処理
}
```

### 3. RESTfulウェブサービスでの実装

リソースメソッドに `@Valid` アノテーションを設定するだけです:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 4. ドメインバリデーション（推奨）

共通のバリデーションルールをドメインBeanにまとめると、メンテナンスコストを低減できます:

```java
// ドメインBeanの作成
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// FormでのDomainアノテーション使用
public class SampleForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;
}
```

### 5. 相関バリデーション

複数フィールドをまたいだチェックは `@AssertTrue` を使います:

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true; // 未入力時はスキップ
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

**注意点**:
- `@OnError` が未設定の場合、バリデーションエラーがシステムエラー扱いになります（必ず設定すること）
- データベースとの相関バリデーション（重複チェック等）はBean Validationではなく業務アクション側で実装すること（バリデーション前の未検証値でDBアクセスするとSQLインジェクションのリスクがあるため）
- バリデーション実行順序は保証されないため、相関バリデーションでは各フィールドが未入力の場合でも例外が発生しない実装にすること

参照: `libraries-bean-validation.json#s8`, `libraries-bean-validation.json#s6`, `libraries-bean-validation.json#s16`, `handlers-InjectForm.json#s3`, `handlers-jaxrs-bean-validation-handler.json#s4`, `libraries-bean-validation.json#s9`, `libraries-bean-validation.json#s11`