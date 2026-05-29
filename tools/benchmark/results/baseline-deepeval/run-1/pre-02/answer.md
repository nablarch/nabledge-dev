内容を確認しました。回答を生成します。

---

**結論**: ウェブアプリケーションの入力チェックは、`@InjectForm` インターセプタを使用する。Formクラスに Bean Validation アノテーションを設定し、アクションメソッドに `@InjectForm` と `@OnError` を付与することで、バリデーションとエラー遷移を自動化できる。

**根拠**:

### 1. コンポーネント設定（Bean Validation有効化）

`BeanValidationStrategy` を `validationStrategy` という名前でコンポーネント定義する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスの作成

Formクラスの**全プロパティはString型**で定義すること（型変換はバリデーション後に行う）。

**ドメインバリデーション（推奨）**: ドメインBeanにルールを集約し、各Formから参照する。

```java
// ドメインBean（バリデーションルールを一元管理）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManager（ドメインBeanを有効化）
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
    @Override
    public Class<SampleDomainBean> getDomainBean() {
        return SampleDomainBean.class;
    }
}
```

```xml
<!-- コンポーネント名は domainManager とすること -->
<component name="domainManager" class="sample.SampleDomainManager"/>
```

Formクラスでは `@Domain` でドメイン名を指定し、`@Required` は個別に付与する。

```java
public class UserForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;

    // getter、setter
}
```

### 3. アクションメソッドへの @InjectForm 設定

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

HTMLのinput name属性は `form.` プレフィックスを付ける。

```html
<input name="form.userName" type="text" />
<input name="form.birthday" type="text" />
```

### 4. エラーメッセージの定義

アノテーションのデフォルトメッセージIDをキーにプロパティファイルで定義する。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必須項目です。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

### 5. 相関バリデーション

複数項目の相関チェックは `@AssertTrue` アノテーションをgetterメソッドに付与する。

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
- DBとの相関バリデーションは **Formに書かず、業務アクション側で実装すること**。Bean Validation実行中はバリデーション前の値でDBアクセスが行われるため、SQLインジェクションの脆弱性リスクがある。
- Jakarta Bean Validationはバリデーション実行順序が保証されないため、相関バリデーション内で単項目バリデーション未実施のケースを考慮した実装が必要。
- FormクラスのプロパティをString以外の型にすると、不正値送信時にBean変換で例外が発生するため必ずStringとすること。

参照: `libraries-bean-validation.json:s6` `libraries-bean-validation.json:s16` `libraries-bean-validation.json:s8` `libraries-bean-validation.json:s9` `libraries-bean-validation.json:s7` `libraries-bean-validation.json:s11` `libraries-bean-validation.json:s12` `handlers-InjectForm.json:s3`

---