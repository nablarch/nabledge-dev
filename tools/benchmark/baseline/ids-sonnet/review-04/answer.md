**結論**: Nablarch では **Bean Validation（Jakarta Bean Validation）** を使うのが推奨スタイル。Formクラスにアノテーションを付与するだけで必須・桁数・形式チェックが書ける。さらに「ドメインバリデーション」を使うとルールを一元管理でき、メンテコストが下がる。

---

**根拠**:

**① 推奨はBean Validation**
Nablarch は2種類のバリデーション機能を提供するが、Jakarta EE 準拠で情報が豊富な Bean Validation の使用を推奨している。
(`component/libraries/libraries-validation.json:s1`)

**② 基本の書き方：Formクラスにアノテーションを付ける**
`@Required`（必須）、`@Length`（桁数）、`@SystemChar`（文字種）などのアノテーションをフィールドに並べるだけでチェックが完結する。

```java
public class SampleForm {
  @Required
  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;
}
```
(`component/libraries/libraries-bean_validation.json:s5`)

**③ ドメインバリデーションでさらに楽に**
ドメインBean にルールをまとめ、各Formでは `@Domain("ドメイン名")` と書くだけにできる。ルール変更時もドメインBean だけ直せばよい。

```java
// ドメインBean（ルール定義）
public class SampleDomainBean {
    @Length(max = 10) @SystemChar(charsetDef = "全角文字")
    String name;
}

// 各Form（ドメイン名を指定するだけ）
public class SampleForm {
    @Domain("name") @Required
    private String userName;
}
```
`@Required` はドメインBean 側ではなく各Form側に書くこと（必須かどうかは機能設計による）。
(`component/libraries/libraries-bean_validation.json:s6`)

**④ Webアクション側の設定**
業務アクションに `@InjectForm` を付けると、バリデーション実行とFormオブジェクトのリクエストスコープ格納が自動で行われる。

```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
    UserForm form = ctx.getRequestScopedVar("form");
}
```
(`component/handlers/handlers-InjectForm.json:s3`)

コンポーネント設定には `BeanValidationStrategy` の登録も必要：
```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```
(`component/libraries/libraries-bean_validation.json:s13`)

---

**注意点**:
- FormクラスのプロパティはすべてStringで定義すること。String以外の型だと変換失敗で例外が起きる (`component/libraries/libraries-bean_validation.json:s5`)
- Jakarta Bean Validation はバリデーション実行順序を保証しないため、相関バリデーションは単項目バリデーション未実行でも例外が出ないよう実装すること (`component/libraries/libraries-bean_validation.json:s1`)
- ネストしたBeanが含まれる場合は `@Valid` と初期化を忘れると null でバリデーションがスキップされるので注意 (`component/libraries/libraries-bean_validation.json:s5`)

参照: component/libraries/libraries-validation.json:s1, component/libraries/libraries-bean_validation.json:s1, component/libraries/libraries-bean_validation.json:s5, component/libraries/libraries-bean_validation.json:s6, component/libraries/libraries-bean_validation.json:s13, component/handlers/handlers-InjectForm.json:s3