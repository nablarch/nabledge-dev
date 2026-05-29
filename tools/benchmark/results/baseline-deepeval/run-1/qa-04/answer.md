Step 5-7: 回答を生成し、検証します。

---

**結論**: Bean ValidationのFormクラスの単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに記述する方式で実装します。

**根拠**:

## テストクラスの作成

以下3つの条件を満たすテストクラスを作成します。

- テスト対象のFormクラスと同じパッケージに配置する
- クラス名は `<FormクラスExName>Test` とする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

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

    /** その他の単項目精査テスト（日付フォーマットなど） */
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

    /** setter/getterテスト */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

## テストデータの準備

Excelファイル（`UserRegistrationFormTest.xlsx`）をテストソースと**同じディレクトリに同名**で配置します。1テストメソッドにつき1シートを用意し、シート名はテストメソッド名と同名にします。

### 文字種・文字列長テスト用シート（`testCharsetAndLength`）

Excelに以下のカラムを持つ表を作成します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力許容するか（`o` / `x`） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o` / `x`） |

### 項目間精査テスト用シート（`testWholeFormValidation`）

- ID `testShots` の表にテストケース（`title`、`expectedMessageId1`、`propertyName1` など）を記載
- ID `params` の表に対応する入力パラメータを記載

## コンポーネント設定ファイルの準備

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を設定します。Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を**必ず**指定します。

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

**注意点**: `testSetterAndGetter` でテスト可能なプロパティ型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラスのみです。`List<String>` など非対応の型は個別にテストを実装してください。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, s2, s5, s6, s16, s17

---