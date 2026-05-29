**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタと Bean Validation アノテーションを組み合わせて実装する。コンポーネント定義・Formクラス・業務アクションの3箇所の設定が必要。

---

**根拠**:

#### 1. コンポーネント定義（BeanValidationStrategy）

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

#### 2. Formクラスの作成（バリデーションルール設定）

Formクラスのプロパティは**必ずすべて `String` 型**で定義すること（型変換失敗による予期せぬ例外を防ぐため）。

**ドメインバリデーション（推奨）**を使う場合、まずドメインBeanを作成する:

```java
// ドメインBean（プロジェクト共通のバリデーションルール定義）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}
```

DomainManager を実装してコンポーネント定義に登録:

```java
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
    @Override
    public Class<SampleDomainBean> getDomainBean() {
        return SampleDomainBean.class;
    }
}
```

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

Formクラスで `@Domain` アノテーションを使用:

```java
public class SampleForm {
    @Domain("name")
    @Required          // 必須かどうかはドメインBeanではなく個別Formに設定する
    private String userName;

    @Domain("date")
    private String birthday;
    // getter/setter省略
}
```

#### 3. 業務アクションへの設定

`@InjectForm` と `@OnError` アノテーションを設定する。`@OnError` を省略するとバリデーションエラーがシステムエラー扱いになるため必須。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    // リクエストスコープからバリデーション済みのフォームを取得
    UserForm form = ctx.getRequestScopedVar("form");
    // 以降は業務処理
}
```

HTML側でフォームパラメータに `form.` プレフィックスを付ける:

```html
<input name="form.userId" type="text" />
<input name="form.password" type="password" />
```

#### 4. エラーメッセージ定義

アノテーションのデフォルトメッセージIDに対応するメッセージをプロパティファイルに定義する:

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

#### 5. 相関バリデーション

複数項目の相関チェックは `@AssertTrue` を使って実装する。実行順序が保証されないため、対象項目が未入力の場合でも例外が発生しないようにロジックを実装すること。

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
- データベースとの相関バリデーション（DBの値との比較など）は Bean Validation 内では実装しない。バリデーション実行中は値の安全性が保証されず SQLインジェクション等の脆弱性リスクがあるため、必ず業務アクション側でバリデーション済みの値を使って実装すること。
- Formのプロパティを `String` 以外の型にすると、不正値送信時にBean変換が失敗して障害になる。

参照: libraries-bean-validation.json:s16, libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s7, libraries-bean-validation.json:s11, libraries-bean-validation.json:s12, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4

---