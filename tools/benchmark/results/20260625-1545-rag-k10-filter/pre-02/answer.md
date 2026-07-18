### Answer

ウェブアプリケーションでの入力チェック（バリデーション）の実装方法を説明します。

## 基本的な実装方法

### 1. InjectFormインターセプタを使う（推奨）

ウェブアプリケーションでは、**InjectFormインターセプタ**を使うのが標準的な方法です。

**Bean Validationを使う場合**、コンポーネント設定ファイルに以下を定義します：

```xml
<component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />
```

### 2. Formクラスの定義

Beanクラスのプロパティは**必ずString型**で定義してください（外部入力値の型変換前にバリデーションが必要なため）。

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

個別アノテーションよりも**ドメインバリデーション**(`@Domain`)を使うことが推奨されています。

### 3. 一括入力のバリデーション

同一情報を複数入力する場合は、ネストしたBeanに`@Valid`を付けます：

```java
public class SampleBulkForm {

  @Valid
  private List<SampleForm> sampleForm;

  public SampleBulkForm() {
    sampleForm = new ArrayList<>();
  }
}
```

---

## バリデーションを明示的に実行したい場合

InjectFormインターセプタが使えないケース（バリデーションエラーを独自ハンドリングしたい等）では、`ValidatorUtil#validate`を使います。

ウェブアプリケーション向けに、以下のようなユーティリティクラスを共通基盤として作成することが推奨されています：

```java
public final class ProjectValidatorUtil {
    public static <T> T validate(Class<T> beanClass, HttpRequest request) {
        T bean = BeanUtil.createAndCopy(beanClass, request.getParamMap());
        ValidatorUtil.validate(bean);
        return bean;
    }
}
```

> **注意**: `HttpRequest#getParamMap`はアーキテクト向けAPIであり、Actionクラスで直接使うことは禁止されています。そのため上記のようなユーティリティクラスを介して使用してください。

### バリデーションエラー時に任意処理を行う例

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/create.jsp")
public HttpResponse create(HttpRequest request, ExecutionContext context) {

    ProjectForm form;

    try {
        form = ProjectValidatorUtil.validate(ProjectForm.class, request);
    } catch (ApplicationException e) {
        // バリデーションエラー時の任意処理
        throw e;  // @OnErrorで指定した画面へ遷移
    }

    // 以降の業務ロジック
}
```

バリデーションエラーが発生した場合は`ApplicationException`が送出されます。

---

## まとめ

| ケース | 方法 |
|--------|------|
| 通常のウェブアプリ入力チェック | InjectFormインターセプタ + BeanValidationStrategy |
| エラーを独自ハンドリングしたい | `ValidatorUtil#validate`を使った明示的実行 |
| 一括登録など複数Bean | ネストBeanに`@Valid`を付与 |