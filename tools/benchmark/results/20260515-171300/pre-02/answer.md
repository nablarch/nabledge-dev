**結論**: Nablarch 6 での入力チェックは **Jakarta Bean Validation（Bean Validation）** を使用して実装します。フォームクラスにバリデーションアノテーションを付与し、処理方式に応じたインターセプタ/ハンドラでバリデーションを実行します。

**根拠**:

**1. 依存モジュール（pom.xml）**
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-validation-ee</artifactId>
</dependency>
```

**2. フォームクラスの作成**
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
フォームクラスのプロパティは**必ず全て String** で定義します。

**3. ドメインバリデーション（推奨）**

個別アノテーション設定よりもドメインバリデーションを推奨します。
```java
// ドメインBean
public class SampleDomainBean {
  @Length(max = 10)
  @SystemChar(charsetDef = "全角文字")
  String name;
}
```
```java
// フォームクラスでの使用
public class SampleForm {
  @Domain("name")
  @Required
  private String userName;
}
```

**4. ウェブアプリケーションでのバリデーション実行**

`BeanValidationStrategy` をコンポーネント定義に登録後、業務アクションに `@InjectForm` を付与：
```java
@InjectForm(form = UserForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://registerForm.jsp")
public HttpResponse handle(HttpRequest req, ExecutionContext ctx) {
  UserForm form = ctx.getRequestScopedVar("form");
  // バリデーション済みのフォームで業務処理
}
```

**5. RESTful ウェブサービスでのバリデーション実行**

リソースクラスのメソッドに `@Valid` を付与：
```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
  UniversalDao.insert(person);
  return new HttpResponse();
}
```

**6. 相関バリデーション**

`@AssertTrue` を使用：
```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
  if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
    return true;
  }
  return Objects.equals(mailAddress, confirmMailAddress);
}
```

**7. エラーメッセージ定義（messages.properties）**
```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**注意点**:
- フォームクラスのプロパティは必ず `String` で定義すること。他の型を使うと不正な入力値でシステムエラーになる
- 相関バリデーションは項目単体バリデーション完了を前提としてはならない。null チェックを必ず含めること
- データベースとの相関バリデーションを Bean Validation 内で実装してはならない（不安全な値でDBアクセスするため）。バリデーション後の業務アクション側で実装すること
- `@OnError` が設定されていない場合、バリデーションエラーがシステムエラー扱いになるので注意
- Nablarch 独自のバリデーション（Nablarch Validation）も存在するが、Nablarch 6 では Bean Validation の使用を推奨

参照: `libraries-validation` / `libraries-bean-validation#s6` / `libraries-bean-validation#s7` / `libraries-bean-validation#s8` / `libraries-bean-validation#s9` / `libraries-bean-validation#s11` / `libraries-bean-validation#s16` / `libraries-bean-validation#s17` / `handlers-InjectForm#s3` / `handlers-jaxrs-bean-validation-handler#s4`