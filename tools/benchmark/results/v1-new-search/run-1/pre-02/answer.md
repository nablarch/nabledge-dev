十分な情報が集まりました。回答を生成します。

---

**結論**: ウェブアプリケーションの入力値チェックは、`@InjectForm` インターセプタを業務アクションのメソッドに設定することで実装します。バリデーションロジックはFormクラスにBean Validationのアノテーションで定義します。

**根拠**:

### 1. コンポーネント設定（Bean Validationを使う場合）

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスの作成

Formクラスのプロパティは**すべて `String` 型**で定義し、バリデーションアノテーションを設定します。

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

> **推奨**: 個別アノテーション設定よりも、ドメインバリデーションの使用を推奨します。ドメインBeanにルールをまとめ、各Formで `@Domain("name")` のように参照します。

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;
}

// DomainManager実装をコンポーネント定義
// <component name="domainManager" class="sample.SampleDomainManager"/>

// Formクラス側
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

### 3. 業務アクションへの設定

`@InjectForm` アノテーションをリクエスト処理メソッドに設定します。`@OnError` でバリデーションエラー時の遷移先を必ず指定してください（未設定の場合はシステムエラー扱いになります）。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // リクエストスコープからバリデーション済みのフォームを取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

HTMLの入力フォームでは、`prefix` に合わせた名前でパラメータを送信します。

```html
<input name="form.userId" type="text" />
<input name="form.password" type="password" />
```

**注意点**:
- Formクラスのプロパティを `String` 以外の型にすると、不正な値が送信された際にバリデーション実施前に変換処理が失敗して障害になります。型変換はバリデーション実施後に行ってください。
- データベースとの相関バリデーションは、SQLインジェクション防止のため業務アクション側で実装してください（Bean Validationの中では行わないこと）。
- 相関バリデーション（複数項目間の検証）は `@AssertTrue` アノテーションを使用して実装します。

参照: handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16

---