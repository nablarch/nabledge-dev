Step 5: 回答を生成します。

**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに記述する。

**根拠**:

---

### テストクラスの作り方

以下の3つの条件を満たすように作成する。

1. テストクラスのパッケージをテスト対象Formと同じにする
2. クラス名を `<Formクラス名>Test` にする
3. `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査テスト（日付フォーマットなど） */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査テスト（@AssertTrueなど） */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }
}
```

スーパークラスが提供する3種類のテストメソッドを使い分ける：

| メソッド | 用途 |
|---|---|
| `testValidateCharsetAndLength` | 文字種と文字列長の単項目精査 |
| `testSingleValidation` | 上記以外の単項目精査（日付フォーマット等） |
| `testBeanValidation` | 項目間精査（`@AssertTrue` 等） |

---

### テストデータの準備方法

**Excelファイルの配置**: テストソースコードと **同じディレクトリ** に **同じ名前**（拡張子 `.xlsx`）で配置する。全セルの書式は必ず「文字列」に設定すること（数値書式のままだと読み取りが正しく動作しない）。

**文字種・文字列長テスト用シートのカラム構成**（`testValidateCharsetAndLength` 用）:

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか（`o` / `x`） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時エラーメッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時エラーメッセージ |
| `半角英字` 〜 `外字` | 各文字種を許容するか（`o` / `x`） |

---

### コンポーネント設定ファイルの設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する必要がある。Bean Validation使用時は `validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定する。

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"        value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="maxAndMinMessageId"  value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="fixLengthMessageId"  value="{nablarch.core.validation.ee.Length.fixed.message}"/>
  <property name="underLimitMessageId" value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="minMessageId"        value="{nablarch.core.validation.ee.Length.min.message}"/>
  <property name="emptyInputMessageId" value="{nablarch.core.validation.ee.Required.message}"/>
  <property name="characterGenerator">
    <component class="nablarch.test.core.util.generator.BasicJapaneseCharacterGenerator"/>
  </property>
  <property name="validationTestStrategy">
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
</component>
```

**注意点**:
- プロパティとして別のFormを保持する親Form（`<親Form>.<子Form>.<プロパティ名>` の形式でアクセスするもの）には、`testValidateCharsetAndLength` / `testSingleValidation` は使用できない。その場合は独自に精査テストを実装すること。
- Entityは自動生成のためアプリで使わないsetter/getterが存在しうる。Entityの場合はsetter/getterテスト（`testSetterAndGetter`）も必須。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s16, testing-framework-01-entityUnitTestWithBeanValidation.json:s17, testing-framework-01-Abstract.json:s9, testing-framework-01-Abstract.json:s14

---