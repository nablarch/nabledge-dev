**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに外部化して記述する。

**根拠**:

**テストクラスの作成方法**

以下の条件を満たすテストクラスを作成する：

- テスト対象Formと同じパッケージ
- クラス名：`<Form名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form;

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査 */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** その他の単項目精査 */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査 */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    /** setter/getter */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

**テストデータの準備方法**

Excelファイルをテストクラスと同じディレクトリに同じ名前（拡張子のみ `.xlsx`）で格納する。

文字種・文字列長テスト用シートには以下のカラムを定義する：

| カラム | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力許容の有無 |
| `min` / `max` | 最小・最大文字列長 |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o`/`x`） |

**コンポーネント設定ファイルの設定**

テスト用設定ファイルに `EntityTestConfiguration` を定義し、`validationTestStrategy` に `BeanValidationTestStrategy` を指定する：

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"
            value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="emptyInputMessageId"
            value="{nablarch.core.validation.ee.Required.message}"/>
  <property name="characterGenerator">
    <component class="nablarch.test.core.util.generator.BasicJapaneseCharacterGenerator"/>
  </property>
  <property name="validationTestStrategy">
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
</component>
```

**注意点**:
- Excelのすべてのセル書式は文字列に設定すること。文字列以外の書式では正しくデータが読み取れない。
- プロパティとして別のFormを保持するネストしたFormには `testValidateCharsetAndLength` / `testSingleValidation` は使用できない。その場合は独自にテストを実装する。
- `testSetterAndGetter` が対応する型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラス（`Integer`、`Long` 等）およびそれらの配列に限られる。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s9, testing-framework-01-entityUnitTestWithBeanValidation.json:s12, testing-framework-01-entityUnitTestWithBeanValidation.json:s14, testing-framework-01-entityUnitTestWithBeanValidation.json:s17, testing-framework-01-Abstract.json:s14