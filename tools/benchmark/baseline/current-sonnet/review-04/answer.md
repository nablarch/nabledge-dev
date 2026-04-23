**結論**: Nablarch 6 では **Bean Validation**（`nablarch.core.validation.ee` パッケージのアノテーション）を使うのが標準的な書き方で、**ドメインバリデーション**を使うとルールを一箇所にまとめられてメンテナンスが格段に楽になります。

---

**根拠**:

### 1. Form クラスの基本ルール

全プロパティを `String` 型で宣言し、バリデーション通過後に型変換することが必須です。`component/libraries/libraries-bean_validation.json:s5`

```java
public class SampleForm {
    @Domain("name")   // ドメイン名を指定（推奨）
    @Required         // 必須チェックはForm側に書く
    private String userName;

    @Domain("date")
    private String birthday;
}
```

### 2. ドメインBeanに共通ルールを集約（推奨パターン）

`@Length`（桁数）・`@SystemChar`（形式）をドメインBeanに一度だけ書き、各Formから `@Domain("フィールド名")` で参照します。`component/libraries/libraries-bean_validation.json:s6`

```java
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;           // ← フィールド名がドメイン名になる

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}
```

`DomainManager` の実装・XML登録、および `BeanValidationStrategy` をコンポーネント名 `validationStrategy` で登録することで有効化されます。`component/libraries/libraries-bean_validation.json:s6`

```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
<component name="validationStrategy"
           class="nablarch.common.web.validator.BeanValidationStrategy"/>
```

### 3. 個別アノテーションを直接書く場合（参考）

ドメインを使わず個別に書くこともできます。`component/libraries/libraries-bean_validation.json:s4`

```java
@Length(max = 10)
@SystemChar(charsetDef = "全角文字")
@Required
private String userName;

@Length(min = 8, max = 8)
@SystemChar(charsetDef = "半角数字")
private String birthday;
```

ただし実装ミスやメンテコスト増のリスクがあるため、ドメインバリデーションを推奨しています。`component/libraries/libraries-bean_validation.json:s5`

### 4. 相関バリデーション（複数項目の組み合わせチェック）

`@AssertTrue` アノテーションを付けたゲッタで実装します。`component/libraries/libraries-bean_validation.json:s1`

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress)
            || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true;  // どちらかが空なら単体チェックに任せる
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

### 5. エラーメッセージのカスタマイズ

プレースホルダにアノテーション属性名を使えます。`component/libraries/libraries-bean_validation.json:s4`

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Length.min.max.message={min}文字以上{max}文字以内で入力してください。
```

---

**注意点**:

- `@Required` はドメインBeanではなく **各Formクラス側**に書くこと（必須かどうかは機能設計による）。`component/libraries/libraries-bean_validation.json:s6`
- Bean Validation ではバリデーション**実行順序が保証されない**。相関バリデーションは単体チェック前に呼ばれる可能性があるため、対象フィールドが null/空の場合は必ず `true` を返すように実装すること。`component/libraries/libraries-bean_validation.json:s8`
- setterへのアノテーション指定は無効。Field または getter（Property）に設定すること。`component/libraries/libraries-bean_validation.json:s5`
- RESTful Web サービスの場合はアクションメソッドの引数に `@Valid` を付けてバリデーションを実行します。`processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`

参照: component/libraries/libraries-bean_validation.json:s1, component/libraries/libraries-bean_validation.json:s4, component/libraries/libraries-bean_validation.json:s5, component/libraries/libraries-bean_validation.json:s6, component/libraries/libraries-bean_validation.json:s8, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1