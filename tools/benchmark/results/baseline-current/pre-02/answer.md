**結論**: ウェブアプリケーションの入力フォームバリデーションは、`@InjectForm` インターセプタと Bean Validation を組み合わせて実装する。フォームクラスに Bean Validation アノテーションを付与し、業務アクションメソッドに `@InjectForm` を設定することで、リクエスト受信時に自動的にバリデーションが実行される。

**根拠**:

1. コンポーネント設定（XML）
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

2. フォームクラスの実装
```java
public class ClientForm implements Serializable {
    @Required
    @Domain("clientName")
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;
}
```

3. 業務アクションメソッドの実装
```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {
    ClientForm form = context.getRequestScopedVar("form");
    // 業務処理へ
}
```

4. JSP 側の入力タグとエラー表示
```jsp
<n:text name="form.clientName" cssClass="form-control" errorCss="input-error" />
<n:error errorCss="message-error" name="form.clientName" />
```

5. 相関バリデーション（複数項目）
```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

**注意点**:
1. フォームのプロパティは全て `String` 型で宣言すること。String 以外の型にすると、不正値が送信された際に Bean への変換処理がバリデーション前に失敗し、予期せぬ例外が発生する。
2. `@OnError` は必ず設定すること。設定しない場合、バリデーションエラーがシステムエラー扱いになる。
3. バリデーションルールは個別アノテーションより `@Domain` を推奨。個別指定は実装ミスやメンテナンスコストが増大する。
4. データベースとの相関バリデーションは業務アクション側で実装すること。Bean Validation 内でDBアクセスを行うと脆弱性の原因となる。
5. 相関バリデーションの実行順序は保証されない。項目単体のバリデーション前に相関バリデーションが呼ばれる場合があるため、null や未入力の考慮が必須。
6. ドメインBeanの `@Required` は個別フォーム側に設定すること。

参照: `libraries-bean-validation#s6`, `libraries-bean-validation#s7`, `libraries-bean-validation#s8`, `libraries-bean-validation#s9`, `libraries-bean-validation#s11`, `libraries-bean-validation#s16`, `handlers-InjectForm#s3`, `handlers-InjectForm#s4`, `web-application-client-create2#s1`, `web-application-feature-details#s2`