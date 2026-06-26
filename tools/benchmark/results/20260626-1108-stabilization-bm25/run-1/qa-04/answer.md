**結論**: Bean ValidationのFormクラスの単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに定義することで行います。テストクラスは3種のテストメソッド（文字種・文字列長精査、単項目精査、項目間精査）を組み合わせて実装します。

**根拠**:

**1. テストクラスの作成**

以下の条件を満たすテストクラスを作成します。

- パッケージはテスト対象のForm/Entityと同じ
- クラス名は `<Form/Entityクラス名>Test`
- `EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種および文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** 単項目精査テスト（文字種・文字列長以外） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査テスト（@AssertTrueなど） */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    /** setter/getter テスト */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

**2. テストデータ（Excelファイル）の準備**

テストデータはテストクラスと**同じディレクトリ・同じ名前**（拡張子 `.xlsx`）で配置します。

- `testCharsetAndLength` シート（文字種・文字列長精査）:

| propertyName | allowEmpty | min | max | messageIdWhenNotApplicable | 半角英字 | 半角数字 | 全角ひらがな | … |
|---|---|---|---|---|---|---|---|---|
| userName | false | 1 | 10 | {nablarch.core.validation.ee.SystemChar.message} | x | x | x | … |

- `testWholeFormValidation` シート（項目間精査）には `testShots`（テストケース表）と `params`（入力パラメータ表）の2つのIDで定義します。

**3. テスト用コンポーネント設定ファイル**

`EntityTestConfiguration` に `BeanValidationTestStrategy` を指定します。

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
- `testValidateCharsetAndLength` と `testSingleValidation` は、**プロパティとして別のFormを保持するForm（ネストForm）には使用できません**。その場合は独自に精査処理のテストを実装してください。
- 一般的なFormのsetter/getterテストは、リクエスト単体テストで実施できるため、クラス単体テストでは省略可能です（Entityは必須）。

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json:s2`, `s3`, `s4`, `s5`, `s6`, `s7`, `s8`, `s9`, `s10`, `s11`, `s12`, `s13`, `s14`, `s16`, `s17`