セクション内容を読み込みました。回答を生成します。

---

**結論**: ウェブアプリケーションの入力チェックは `@InjectForm` インターセプタを使用して実装する。Bean Validationを利用する場合は、コンポーネント設定に `BeanValidationStrategy` を追加し、Formクラスのフィールドにバリデーションアノテーションを付与する。

---

**根拠**:

### 1. コンポーネント設定

コンポーネント設定ファイルに `BeanValidationStrategy` を `validationStrategy` という名前で定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスの定義

**フォームのプロパティはすべて `String` 型**で定義し、アノテーションでバリデーションルールを設定する（ドメインバリデーションを推奨）。

**ドメインBeanの作成（ルール一元管理）**:

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

**DomainManagerの設定**:

```xml
<!-- DomainManager実装クラスは、domainManagerという名前で設定すること -->
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**Formクラスで `@Domain` アノテーションを使用**:

```java
public class SampleForm {

  @Domain("name")
  @Required          // 必須はForm側に設定する
  private String userName;

  @Domain("date")
  private String birthday;

  // getter、setter省略
}
```

### 3. アクションメソッドへのアノテーション設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

  // バリデーション済みのフォームをリクエストスコープから取得する
  UserForm form = ctx.getRequestScopedVar("form");

  // formを元に業務処理を行う
}
```

- `prefix = "form"` により、HTMLの `form.userId` 等のパラメータがバリデーション対象になる
- バリデーション成功時：`@InjectForm` の `name` で指定したキー名（省略時は `"form"`）でフォームオブジェクトがリクエストスコープに格納される
- `@OnError`：バリデーションエラー時の遷移先を指定する

### 4. エラーメッセージの定義

アノテーションのメッセージIDに対応するメッセージをpropertiesファイルに定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

---

**注意点**:
- Formのプロパティは必ず `String` 型で定義すること。`String` 以外の型を使うと、不正な値が送信された際にBeanへの変換が失敗し、バリデーション前に例外が発生する
- `@OnError` を設定しないと、バリデーションエラーがシステムエラー扱いになるため必ず設定すること
- バリデーションエラー時にもリクエストスコープからフォームを参照したい場合（JSTLタグ等で使用する場合）は、`BeanValidationStrategy` の `copyBeanToRequestScopeOnError` を `true` に設定する

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy">
  <property name="copyBeanToRequestScopeOnError" value="true"/>
</component>
```

参照: libraries-bean-validation.json:s16, libraries-bean-validation.json:s8, libraries-bean-validation.json:s7, libraries-bean-validation.json:s9, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, handlers-on-error.json:s3, libraries-bean-validation.json:s18

---