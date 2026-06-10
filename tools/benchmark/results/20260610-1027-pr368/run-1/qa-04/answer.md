**結論**: Bean Validation対応FormのクラステストはNablarchの自動テストフレームワーク（`EntityTestSupport`継承）を使用し、テストデータはテストクラスと同じディレクトリにExcelファイルとして配置する。

---

**根拠**

## テストクラスの作り方

以下3点を満たすテストクラスを作成する。

- パッケージはテスト対象のFormと同じ
- クラス名は `<FormクラスName>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // Formと同じパッケージ

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
}
```

各テストメソッドに対応するスーパクラスのメソッド：

| テストの種類 | メソッド |
|---|---|
| 文字種・文字列長の単項目精査 | `testValidateCharsetAndLength(Class, String, String)` |
| その他の単項目精査 | `testSingleValidation(Class, String, String)` |
| 項目間精査 | `testBeanValidation(Class, String)` |

---

## テストデータの準備方法

**Excelファイルの配置場所**:
テストソースコードと同じディレクトリに、**同じファイル名**（拡張子のみ `.xlsx`）で配置する。

例：
- テストクラス: `test/com/example/form/UserRegistrationFormTest.java`
- テストデータ: `test/com/example/form/UserRegistrationFormTest.xlsx`

**文字種・文字列長テスト用のExcelシート構成（`testCharsetAndLength` シート）**:

| propertyName | allowEmpty | min | max | 半角英字 | 半角数字 | 全角カタカナ | … |
|---|---|---|---|---|---|---|---|
| userName | x |  | 50 | o | o | o | … |

`allowEmpty`欄には必須項目の場合 `x`（許容しない）、任意項目は `o` を記入する。各文字種カラムには許容する場合 `o`、許容しない場合 `x` を記入する。

**コンポーネント設定ファイルの設定（必須）**:

テスト用コンポーネント設定ファイルに以下の `EntityTestConfiguration` 設定を追加する。

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"
            value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="maxAndMinMessageId"
            value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="fixLengthMessageId"
            value="{nablarch.core.validation.ee.Length.fixed.message}"/>
  <property name="underLimitMessageId"
            value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="minMessageId"
            value="{nablarch.core.validation.ee.Length.min.message}"/>
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

Bean Validationを使用する場合は `validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定する。

**注意点**:
- Excelのセルの書式は必ず**文字列**形式で設定すること（文字列以外だとデータが正しく読み込まれない）
- テストメソッドの実行順序に依存しないテストを作成すること（各テストが必要な事前条件を自テストクラス内で準備する）
- プロパティとして別のFormを保持する親Formには `testValidateCharsetAndLength` / `testSingleValidation` は使用できない。その場合は独自に実装する

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s6, s9, s12, s16, s17