**結論**: ウェブアプリケーションでの入力チェックは、`@InjectForm` インターセプタを業務アクションのメソッドに付与し、Formクラスに Bean Validation アノテーションを設定することで実装します。

**根拠**:

**Step 1: コンポーネント設定ファイルに `BeanValidationStrategy` を定義する**

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**Step 2: Formクラスにバリデーションルールを設定する**

Formクラスのプロパティは **必ず `String` 型で宣言**すること。アノテーションはフィールドまたはgetterに設定する（setterには無効）。

ドメインバリデーション（推奨）を使う場合は、ドメインBeanを先に定義する:

```java
// ドメインBean
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManagerの作成とコンポーネント設定
// <component name="domainManager" class="sample.SampleDomainManager"/>
```

FormクラスでDomainアノテーションを使う:

```java
public class ClientForm implements Serializable {

    @Required
    @Domain("name")
    private String clientName;

    @Domain("date")
    private String birthday;

    // getter、setter省略
}
```

**Step 3: 業務アクションに `@InjectForm` と `@OnError` を付与する**

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {

    // バリデーション済みオブジェクトをリクエストスコープから取得
    ClientForm form = context.getRequestScopedVar("form");

    // 業務処理を実行
}
```

- `prefix = "form"` は `form.clientName` のようにHTMLのname属性のプレフィックスと一致させる
- バリデーション成功時、バリデーション済みフォームがリクエストスコープ（デフォルトキー名: `"form"`）に格納される

**Step 4: エラーメッセージをプロパティファイルに定義する**

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- `@OnError` を設定しないとバリデーションエラーがシステムエラー扱いになるため、必ず付与すること
- Formプロパティを `String` 以外の型にすると、不正な入力値でBeanへの変換が失敗し障害につながる
- データベースとの相関バリデーションは、SQLインジェクション防止のため業務アクション側で実装すること（Bean Validationの中でDBアクセスを行わない）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, libraries-bean-validation.json:s9, libraries-bean-validation.json:s7, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4