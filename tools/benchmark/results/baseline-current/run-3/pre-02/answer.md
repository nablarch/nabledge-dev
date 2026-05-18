**結論**: Nablarch 6 では **Jakarta Bean Validation（Bean Validation）** を使って入力チェックを実装します。Nablarch独自のバリデーション（Nablarch Validation）も利用可能ですが、Jakarta EE標準で情報が豊富なBean Validationの使用が推奨されています。

**根拠**:

**1. 依存関係の追加（pom.xml）**
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-validation-ee</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-message</artifactId>
</dependency>
```

**2. Formクラスへのアノテーション設定**

プロパティは必ず `String` 型で定義し、アノテーションでルールを設定します：

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

**3. ドメインバリデーション（推奨）**

個別アノテーションよりも、ドメインBeanを作成してルールを集中管理する方法が推奨されています：

```java
// ドメインBeanを定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// Formでドメインを参照
public class SampleForm {
    @Domain("name")
    @Required
    private String userName;
}
```

**4. Webアプリケーションでの使用**

`@InjectForm` インターセプタをアクションメソッドに設定します：

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
    // バリデーション済みのformを使って業務処理
}
```

コンポーネント設定に `BeanValidationStrategy` の定義も必要：
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**5. 相関バリデーション**

`@AssertTrue` を使ったメソッドで実装します：
```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

データベースとの相関バリデーションはアクション側で実装（Bean Validation内でのDBアクセスは禁止）。

**注意点**:
- Formクラスのプロパティは必ずString型にすること（数値型などにすると変換失敗で予期せぬ例外が発生）
- @Required はドメインBeanではなく個別のFormクラス側に設定すること
- @OnError アノテーションを必ず設定すること（未設定だとバリデーションエラーがシステムエラー扱いになる）
- 明示的なバリデーション実行は ValidatorUtil#validate(form) で可能（エラー時は ApplicationException が送出される）

参照: libraries-validation.json / libraries-bean-validation.json#s8,s9,s11,s16 / handlers-InjectForm.json#s3