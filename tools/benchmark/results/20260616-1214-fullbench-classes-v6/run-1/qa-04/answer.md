**結論**: Bean Validation対応のForm/Entity単体テストは、`EntityTestSupport`を継承したテストクラスと、同一ディレクトリに配置したExcelファイルの組み合わせで作成する。

**根拠**:

### テストクラスの作成

以下の条件を満たすテストクラスを作成する。
- パッケージはテスト対象のFormと同じにする
- クラス名は `<Formクラス名>Test` にする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form;

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** その他の単項目精査テスト */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査テスト */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    /** setter/getterテスト */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

### テストデータの準備

Excelファイルはテストクラスと**同じディレクトリに同じ名前**で格納する（拡張子のみ `.xlsx`）。例えば `UserRegistrationFormTest.java` に対して `UserRegistrationFormTest.xlsx` を作成する。

**文字種・文字列長テスト（testCharsetAndLength シート）の主なカラム:**

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| allowEmpty | 未入力を許容するか (o/x) |
| min / max | 最小・最大文字列長 |
| messageIdWhenNotApplicable | 文字種不適合時のメッセージ |
| 半角英字〜外字 | 各文字種を許容するか (o/x) |

### フレームワーク設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する。Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を必ず指定する。

```xml
<component name="entityTestConfiguration" class="nablarch.test.core.entity.EntityTestConfiguration">
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

**注意点**: `testValidateCharsetAndLength` はプロパティとして別のFormを保持するForm（親Form.子Form.プロパティ形式でアクセスするForm）には使用できない。その場合は独自に精査処理のテストを実装すること。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s15, s16, s17