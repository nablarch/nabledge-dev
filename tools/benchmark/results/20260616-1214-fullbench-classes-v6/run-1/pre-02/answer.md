**結論**: ウェブアプリケーションの入力チェックは `@InjectForm` インターセプタとBean Validationを組み合わせて実装する。Formクラスにバリデーションアノテーションを設定し、業務アクションメソッドに `@InjectForm` を付与することでバリデーションが自動実行される。

**根拠**:

**1. コンポーネント設定ファイルの準備**

`BeanValidationStrategy` を `validationStrategy` という名前で登録する。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

**2. Formクラスの実装**

プロパティは**必ずString型**で定義し、バリデーションアノテーションを付与する。ドメインバリデーションの使用を推奨。

```java
public class ClientForm implements Serializable {

    @Required
    @Domain("clientName")   // ドメインバリデーション使用推奨
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;

    // getter、setter省略
}
```

ドメインBeanとDomainManagerの定義:

```java
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String clientName;

    @Length(max = 2)
    @SystemChar(charsetDef = "半角数字")
    String industryCode;
}
```

```xml
<!-- domainManagerという名前で登録 -->
<component name="domainManager" class="sample.SampleDomainManager"/>
```

**3. 業務アクションへの`@InjectForm`設定**

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {

    // バリデーション済みフォームをリクエストスコープから取得
    ClientForm form = context.getRequestScopedVar("form");

    // 以降、業務処理を行う
}
```

ポイント:
- `prefix = "form"` は `form.xxx` という名前のリクエストパラメータをバリデーション対象とする
- `@OnError` を必ず設定すること。未設定の場合バリデーションエラーがシステムエラー扱いになる
- バリデーション済みフォームは `ctx.getRequestScopedVar("form")` で取得できる

**注意点**:
- Formのプロパティは全てString型にすること。String以外の型だと変換失敗時に予期せぬ例外が発生する
- `@Required` アノテーションはドメインBeanに設定せず、各Formクラス側に設定すること（必須かどうかは機能設計による）
- データベースとの相関バリデーション（重複チェック等）はBean Validationではなく業務アクション側で実装すること（バリデーション前の安全でない値でDBアクセスするとSQLインジェクションリスクがある）

参照: libraries-bean-validation.json:s8, libraries-bean-validation.json:s16, libraries-bean-validation.json:s9, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4