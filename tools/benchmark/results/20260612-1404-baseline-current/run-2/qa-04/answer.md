**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに記述して専用メソッド（`testValidateCharsetAndLength` / `testSingleValidation`）を呼び出す方式で実装する。

**根拠**:

## テストクラスの作り方

以下の3条件を満たすテストクラスを作成する。

- テスト対象のFormクラスと**同じパッケージ**にする
- クラス名は `<Form名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種および文字列長の単項目精査テストケース */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** 単項目精査テストケース（上記以外） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査のテストケース */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }
}
```

テストの種別と対応するスーパークラスのメソッド:

| テスト対象 | 使用メソッド |
|---|---|
| 文字種・文字列長の単項目精査 | `testValidateCharsetAndLength(Class, String, String)` |
| その他の単項目精査（日付フォーマット等） | `testSingleValidation(Class, String, String)` |
| 項目間精査（`@AssertTrue` 等） | `testBeanValidation(Class, String)` |

## テストデータの準備方法

**Excelファイルの配置**: テストソースコードと**同じディレクトリ**に、**同じ名前**（拡張子のみ `.xlsx`）で配置する。

**文字種・文字列長テスト用Excelシートの主なカラム**:

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| allowEmpty | 未入力を許容するか（`o`/`x`） |
| min | 最小文字列長（省略可） |
| max | 最大文字列長（省略可） |
| messageIdWhenEmptyInput | 未入力時の期待メッセージ（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時の期待メッセージ |
| 半角英字〜外字 | 各文字種を許容するか（`o`/`x`） |

## 必要な設定（コンポーネント設定ファイル）

Bean Validationを使用する場合、テスト用コンポーネント設定ファイルに以下を追加する。

```xml
<component name="entityTestConfiguration" class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"        value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="maxAndMinMessageId"  value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="fixLengthMessageId"  value="{nablarch.core.validation.ee.Length.fixed.message}"/>
  <property name="underLimitMessageId" value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="minMessageId"        value="{nablarch.core.validation.ee.Length.min.message}"/>
  <property name="emptyInputMessageId" value="{nablarch.core.validation.ee.Required.message}"/>
  <property name="characterGenerator">
    <component name="characterGenerator"
               class="nablarch.test.core.util.generator.BasicJapaneseCharacterGenerator"/>
  </property>
  <property name="validationTestStrategy">
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
</component>
```

`validationTestStrategy` は Bean Validation 使用時は `BeanValidationTestStrategy` を固定で指定する。

**注意点**: メッセージデータやコードマスタなどの静的マスタデータは、個別テストデータとして用意するのではなく、プロジェクトで管理されたデータがあらかじめDBに投入されている前提で作成する。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s16, testing-framework-01-entityUnitTestWithBeanValidation.json:s17