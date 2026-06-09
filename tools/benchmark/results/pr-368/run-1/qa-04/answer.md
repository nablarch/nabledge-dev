**結論**: Bean Validation対応FormクラスのテストはNablarch自動テストフレームワークで提供される `EntityTestSupport` を継承したテストクラスを作成し、テストデータはテストクラスと同名のExcelファイルで準備します。

---

**根拠**:

## テストクラスの作成

以下の条件でテストクラスを作成します。

- テストクラスのパッケージはテスト対象Formと**同じ**にする
- クラス名は `<Form名>Test` にする
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

    /** その他の単項目精査テスト（日付フォーマット等） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査テスト（@AssertTrue等） */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }
}
```

---

## テストデータの準備（Excelファイル）

Excelファイルは**テストクラスと同じディレクトリ・同じ名前**（拡張子のみ `.xlsx`）で配置します。

### 文字種・文字列長テスト用シートのカラム構成

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `group` | Bean Validationのグループ（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `半角数字`, ... `外字` | 各文字種を許容するか（`o` or `x`） |

### 項目間精査テスト用シートのカラム構成

- テストケース表のID：`testShots`（固定）
- 入力パラメータ表のID：`params`（固定）
- `expectedMessageId1` + `propertyName1` でエラーを期待するプロパティとメッセージを指定

---

## フレームワーク設定（コンポーネント設定ファイル）

Bean Validationを使用する場合、テスト用コンポーネント設定に `BeanValidationTestStrategy` を指定する必要があります。

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

---

**注意点**: メッセージデータやコードマスタなどの静的マスタデータは、プロジェクトで管理されたデータがあらかじめDBに投入されている前提です。個別のテストデータとして作成しません。また、プロパティとして別のFormを保持するFormには本テスト方法は使用できません。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s4, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s16, testing-framework-01-entityUnitTestWithBeanValidation.json:s17