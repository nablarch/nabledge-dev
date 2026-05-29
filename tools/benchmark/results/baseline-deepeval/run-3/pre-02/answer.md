Step 4: セクション読み取りが完了しました。必要なセクションの内容はすでに取得済みです。Step 5でStep 3の選択セクションを用いて回答を生成します。

**Step 3 セクション選定まとめ:**
- `libraries-bean-validation.json:s8` HIGH - バリデーションルールをアノテーションで設定する方法
- `libraries-bean-validation.json:s9` HIGH - ドメインバリデーション（推奨方式）
- `libraries-bean-validation.json:s16` HIGH - ウェブアプリでの具体的な実装方法（`InjectForm`使用）
- `handlers-InjectForm.json:s3` HIGH - `@InjectForm`の使用方法
- `handlers-InjectForm.json:s4` HIGH - バリデーションエラー時の遷移先設定
- `libraries-bean-validation.json:s6` PARTIAL - Bean Validationを使うための設定
- `libraries-bean-validation.json:s7` PARTIAL - エラーメッセージ定義
- `web-application-error-message.json` PARTIAL - エラーメッセージ表示

**Step 6 verify実行**: 回答内のNablarch固有のクレームを確認します。

- `@InjectForm`アノテーション → `handlers-InjectForm.json:s3`で直接記述あり ✓
- `BeanValidationStrategy`の設定 → `libraries-bean-validation.json:s16`で直接記述あり ✓
- `@OnError`アノテーション → `handlers-InjectForm.json:s4`と`s3`で直接記述あり ✓
- `context.getRequestScopedVar("form")` → `handlers-InjectForm.json:s3`で直接記述あり ✓
- `@Required`, `@Domain`, `@Length`, `@SystemChar` → `libraries-bean-validation.json:s7`, `s8`, `s9`で直接記述あり ✓
- Formのプロパティは全てString型 → `libraries-bean-validation.json:s8`で直接記述あり ✓

verify_result = PASS

---

**結論**: ウェブアプリケーションの入力値チェックは、`@InjectForm` インターセプタとBean Validationを組み合わせて実装する。FormクラスにアノテーションでバリデーションルールをField/Propertyに設定し、アクションメソッドに`@InjectForm`を付与することでフレームワークが自動的にバリデーションを実行する。

**根拠**:

### 1. コンポーネント設定ファイルにBean Validationストラテジを登録する

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスにバリデーションルールを設定する

Formクラスの**プロパティは全てString型**で宣言すること。バリデーションルールはFieldまたはProperty(getter)にアノテーションで指定する。

**個別アノテーションで設定する場合**:
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

**ドメインバリデーション（推奨）を使う場合**:

まずドメインBeanを作成する:
```java
// ドメインごとのバリデーションルールを定義
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}
```

`DomainManager`実装クラスを作成してコンポーネント定義する:
```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

Formクラスでは`@Domain`アノテーションでドメイン名を指定するだけ:
```java
public class SampleForm {
    @Domain("name")
    @Required
    private String userName;

    @Domain("date")
    private String birthday;
}
```

### 3. アクションメソッドに `@InjectForm` を付与する

```java
@InjectForm(form = UserForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {

    // リクエストスコープからバリデーション済みのフォームを取得する
    UserForm form = ctx.getRequestScopedVar("form");

    // formを元に業務処理を行う
}
```

- `form` 属性: バリデーション対象のFormクラスを指定
- `prefix` 属性: リクエストパラメータのプレフィックス（例: `form.userName`）
- `@OnError`: **必須**。設定がない場合、バリデーションエラーがシステムエラー扱いになる

### 4. エラーメッセージを定義する

```properties
# アノテーション対応メッセージ
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

### 5. エラーメッセージを画面に表示する（Thymeleaf例）

```html
<!-- 特定項目のエラーメッセージ -->
<span th:if="${errors.hasError('form.userName')}"
      th:text="${errors.getMessage('form.userName')}">入力してください。</span>

<!-- 全エラーメッセージ -->
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

**注意点**:
- `@Required`アノテーションはドメインBeanではなく、個別のFormクラス側に設定すること（必須かどうかは機能設計による）
- バリデーションの実行順序はBean Validationでは保証されないため、相関バリデーションは単独バリデーションの完了を前提とした実装は行わないこと
- データベースとの相関バリデーションはSQLインジェクション防止のため、バリデーション済みの値を使用して業務アクション側で実装すること

参照: libraries-bean-validation.json:s6, libraries-bean-validation.json:s7, libraries-bean-validation.json:s8, libraries-bean-validation.json:s9, libraries-bean-validation.json:s16, handlers-InjectForm.json:s3, handlers-InjectForm.json:s4, web-application-error-message.json

---