**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータはExcelファイルに記述する形式で行います。

**根拠**:

#### テストクラスの作り方

以下の条件を満たすテストクラスを作成します。

- パッケージはテスト対象のForm/Entityと同じにする
- クラス名は `<Form/Entityクラス名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form;

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // 文字種・文字列長の単項目精査テスト
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    // その他の単項目精査テスト（日付フォーマット等）
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    // 項目間精査テスト（@AssertTrue等）
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    // setter/getterテスト
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

#### テストデータの準備方法

テストデータはExcelファイルに記述します。Excelファイルはテストソースコードと同じディレクトリに、**同じ名前（拡張子のみ `.xlsx`）** で格納します。

**文字種・文字列長テスト用シート (`testCharsetAndLength`)** の主要なカラム：

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小/最大文字列長 |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `全角カタカナ`, ... | 各文字種を許容するか（`o`/`x`） |

**その他の単項目精査シート (`testSingleValidation`)** のカラム：

| カラム名 | 内容 |
|---|---|
| `propertyName` | プロパティ名 |
| `case` | ケース説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージ（エラーなしは空欄） |

**項目間精査シート (`testWholeFormValidation`)** は、テストケース表（ID: `testShots`）と入力パラメータ表（ID: `params`）の2つを同一シートに記述します。

#### 設定ファイルの準備

コンポーネント設定ファイルに `EntityTestConfiguration` の設定が必要です（Bean Validationの場合は `validationTestStrategy` に `BeanValidationTestStrategy` を指定）。

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

**注意点**: `testSetterAndGetter` でテスト可能なプロパティ型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラス（`Integer`、`Long` 等）に限定されます。それ以外の型（`List<String>` 等）は個別にsetterとgetterを呼び出してテストする必要があります。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, s2, s6, s8, s9, s12, s13, s14, s16, s17