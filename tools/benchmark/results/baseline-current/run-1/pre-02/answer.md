**結論**: Nablarch 6 では **Bean Validation**（Jakarta Bean Validation）を使った入力チェックが推奨されます。Formクラスのフィールドにバリデーションアノテーションを付与し、ウェブアプリは `InjectForm` インターセプタ、RESTfulサービスは `@Valid` アノテーションで実行します。

**根拠**:

### 1. Formクラスの実装（バリデーションルール設定）

フィールドにアノテーションを付与します。**プロパティの型は必ず `String`** にしてください。

```java
public class SampleForm {

  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  @Required
  private String userName;

  @Length(min = 8, max = 8)
  @SystemChar(charsetDef = "半角数字")
  private String birthday;

  // getter、setter
}
```

### 2. ドメインバリデーション（推奨）

個別アノテーションより、**ドメインバリデーション**の使用が推奨されます。ドメインBeanでルールを一元管理できます。

```java
// ドメインBean（ルール定義）
public class SampleDomainBean {
    @Length(max = 10)
    @SystemChar(charsetDef = "全角文字")
    String name;

    @Length(min = 8, max = 8)
    @SystemChar(charsetDef = "半角数字")
    String date;
}

// DomainManager実装
public class SampleDomainManager implements DomainManager<SampleDomainBean> {
  @Override
  public Class<SampleDomainBean> getDomainBean() {
      return SampleDomainBean.class;
  }
}
```

コンポーネント設定ファイル:
```xml
<component name="domainManager" class="sample.SampleDomainManager"/>
```

各Formでの使用:
```java
public class SampleForm {
  @Domain("name")
  @Required           // @Required はドメインBeanではなくForm側に設定
  private String userName;

  @Domain("date")
  private String birthday;
}
```

### 3. ウェブアプリケーションでの実行

`BeanValidationStrategy` をコンポーネント定義し、`InjectForm` インターセプタ経由で実行されます。

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 4. RESTfulウェブサービスでの実行

アクションメソッドに `@Valid` アノテーションを付与します。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

### 5. エラーメッセージの定義

メッセージプロパティファイルにアノテーションのメッセージIDをキーとして定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.SystemChar.message={charsetDef}を入力してください。
```

**注意点**:
- Formのプロパティは**必ず `String` 型**にすること。`String` 以外の型にすると、不正な入力値がBeanへの変換時に例外となり障害になります
- `@Required` アノテーションはドメインBeanではなく、**個々のFormクラス側**に設定すること（必須かどうかは機能設計による）
- アノテーションは **Field か Property（getter）** に設定する（setterへの設定は無効）
- クライアントサイドバリデーション済みの値でも、**サーバサイドバリデーションは必須**（JavaScriptの無効化・改竄対策）

参照: `component/libraries/libraries-bean-validation.json#s8`, `component/libraries/libraries-bean-validation.json#s9`, `component/libraries/libraries-bean-validation.json#s16`, `component/handlers/handlers-jaxrs-bean-validation-handler.json#s4`