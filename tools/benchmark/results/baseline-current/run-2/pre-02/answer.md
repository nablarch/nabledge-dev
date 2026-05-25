**結論**: Nablarch 6 の入力チェックには **Bean Validation**（推奨）と **Nablarch Validation** の2種類があります。ウェブアプリケーションでは `@InjectForm` インターセプタと組み合わせて使います。

## Bean Validation（推奨）

### 1. コンポーネント設定

ウェブアプリケーションで Bean Validation を使うには、`BeanValidationStrategy` をコンポーネント定義します。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. フォームクラスの実装

アノテーションを **Field または getter** に設定します。プロパティの型は**すべて `String`** で定義してください（外部入力値を別の型にする場合はバリデーション後に変換）。

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

Nablarch が提供するバリデータは `nablarch.core.validation.ee` および `nablarch.common.code.validator.ee` パッケージのアノテーションを参照してください。

### 3. ウェブアクションへの適用（`@InjectForm`）

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");

    // form を元に業務処理を実行
}
```

HTML 側では `form.` プレフィックスをパラメータ名に付与します。

```html
<!-- バリデーション対象外 -->
<input name="flag" type="hidden" />

<!-- バリデーション対象 -->
<input name="form.userId" type="text" />
<input name="form.password" type="password" />
```

## Nablarch Validation（レガシー）

バリデーションルールは **setter** にアノテーションを設定します（getter には設定不可）。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  public void setUserName(String userName) { this.userName = userName; }

  @ValidateFor("validate")
  public static void validate(ValidationContext<SampleForm> context) {
      ValidationUtil.validate(context, new String[] {"userName", "birthday"});
  }
}
```

実行方法：

```java
ValidationContext<SampleForm> validationContext =
    ValidationUtil.validateAndConvertRequest(SampleForm.class, request, "validate");

validationContext.abortIfInvalid(); // エラー時に例外をスロー
SampleForm form = validationContext.createObject();
```

**注意点**:

- Bean Validation では **setter にアノテーションを設定しても無視**されます（Field か getter に設定すること）
- Nablarch Validation では逆に **getter にアノテーションを設定しても無視**されます（setter に設定すること）
- プロパティは**必ず `String` 型**にすること。`String` 以外の型に不正な値が入力されるとバリデーション前に変換例外が発生します
- ウェブアプリケーションでは `@InjectForm` + `BeanValidationStrategy` の組み合わせが最もシンプルです

参照: component/handlers/handlers-InjectForm.json#s3, component/libraries/libraries-bean-validation.json#s6, component/libraries/libraries-bean-validation.json#s8, component/libraries/libraries-bean-validation.json#s16, component/libraries/libraries-nablarch-validation.json#s8, component/libraries/libraries-nablarch-validation.json#s11