**結論**: Nablarch 6でのバリデーション実装には、主に**Bean Validation（Jakarta Bean Validation）**を使用します。Formクラスのフィールドにアノテーションを設定し、処理方式（Webアプリ・RESTful）に応じた仕組みで自動実行されます。

**根拠**:

### 1. 基本的なバリデーションルールの設定

Formクラスのフィールド（またはgetter）にアノテーションを設定します。**フィールドの型は必ず`String`で定義すること**（型変換失敗を防ぐため）。

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

Nablarchが提供する主なバリデータは `nablarch.core.validation.ee` パッケージのアノテーションを参照してください。

### 2. ドメインバリデーション（推奨）

個別にアノテーションを設定するより、ドメイン単位でルールを一元管理できるため推奨です。

**① ドメインBeanを作成**:
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

**② DomainManagerを実装してコンポーネント登録**:
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

**③ FormクラスでDomainアノテーションを使用**:
```java
public class SampleForm {
    @Domain("name")
    @Required      // 必須チェックはForm側で設定すること
    private String userName;

    @Domain("date")
    private String birthday;
}
```

### 3. Webアプリケーションでのバリデーション実行

`InjectFormインターセプタ`が自動的にバリデーションを実行します。コンポーネント設定ファイルに以下を追加：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 4. RESTfulウェブサービスでのバリデーション実行

リソースクラスのメソッドに`@Valid`アノテーションを設定することで実行されます。

### 5. エラーメッセージの定義

デフォルトではNablarchのメッセージ管理を使用します。プロパティファイルにメッセージIDをキーとして定義：

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=必ず入力してください。
```

### 6. 相関バリデーション

`@AssertTrue`アノテーションをgetterメソッドに設定して実装します：

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true; // 片方が未入力の場合は検証しない
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```

### 7. バリデーションの明示的な実行

通常の仕組みが使えない場合は`ValidatorUtil#validate`を使用：

```java
ValidatorUtil.validate(form);
// エラー時はApplicationExceptionがスローされる
```

**注意点**:
- フィールドの型は**必ず`String`**で定義すること。`int`等の型を使うと型変換失敗で予期せぬ例外が発生する
- `@Required`（必須チェック）はドメインBeanではなく**Formクラス側**に設定すること（必須かどうかはドメインではなく機能設計による）
- 相関バリデーションはJakarta Bean Validationの実行順序が保証されないため、項目単体バリデーション前に呼ばれる場合を考慮してnullチェックを実装すること
- Webアプリでの明示的バリデーション実行は、バリデーション前の入力値を直接扱うリスクがあるため、アーキテクト向けAPIを使った共通ユーティリティとして実装すること

参照: `component/libraries/libraries-bean-validation.json#s8`, `component/libraries/libraries-bean-validation.json#s9`, `component/libraries/libraries-bean-validation.json#s11`, `component/libraries/libraries-bean-validation.json#s16`, `component/libraries/libraries-bean-validation.json#s17`, `component/libraries/libraries-bean-validation.json#s20`, `component/libraries/libraries-bean-validation.json#s7`