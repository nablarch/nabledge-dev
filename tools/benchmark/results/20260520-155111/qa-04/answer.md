**結論**: `EntityTestSupport` を継承したテストクラスを作成し、テストデータはExcelファイルで管理します。クラス名は `<FormクラスX名>Test`、Excelファイルはテストクラスと同一ディレクトリ・同一名（拡張子のみ `.xlsx`）で配置します。

**根拠**:

**テストクラスの作り方**

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    // Formクラス名 + "Test" のクラス名で EntityTestSupport を継承する

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査テスト */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査テスト（@AssertTrue等） */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }

    /** setter/getterテスト */
    @Test
    public void testSetterAndGetter() {
        testSetterAndGetter(TARGET_CLASS, "testSetterAndGetter", "setterAndGetter");
    }
}
```

**テストデータの準備方法**

Excelファイルをテストクラスと同一ディレクトリに `UserRegistrationFormTest.xlsx` として配置します。シートは以下の単位で作成します。

1. **文字種・文字列長テスト用シート** (`testCharsetAndLength`)
   - カラム: `propertyName`、`allowEmpty`、`min`、`max`、`messageIdWhenEmptyInput`、`messageIdWhenInvalidLength`、`messageIdWhenNotApplicable`、および各文字種（半角英字・半角数字・全角カタカナ等）
   - 許容する文字種に `o`（半角英小文字のオー）、許容しない文字種に `x` を設定

2. **その他単項目精査テスト用シート** (`testSingleValidation`)
   - カラム: `propertyName`、`case`、`input1`、`messageId`
   - 精査エラーにならない場合は `messageId` を空欄にする

3. **項目間精査テスト用シート** (`testWholeFormValidation`)
   - `testShots` テーブル（`title`、`description`、`expectedMessageId1`、`propertyName1` 等）と `params` テーブル（入力パラメータ）を用意

**フレームワーク設定（コンポーネント設定ファイル）**

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

**注意点**: 
- `validationTestStrategy` には Bean Validation 使用時は必ず `BeanValidationTestStrategy` を指定すること。
- バリデーションエラーメッセージ等の静的マスタデータはプロジェクト共通データとして事前にDBへ投入されている前提のため、個別テストデータとして作成しない。
- `testSetterAndGetter` でテスト可能なプロパティの型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラスに限られる。`List<String>` 等それ以外の型は個別にテストを実装すること。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s4, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s15, testing-framework-01-entityUnitTestWithBeanValidation.json:s16, testing-framework-01-entityUnitTestWithBeanValidation.json:s17