**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイル（テストクラスと同ディレクトリ・同名の `.xlsx`）に記述して実行する。

---

**根拠**:

#### テストクラスの作り方

以下の3条件を満たすテストクラスを作成する。

- テスト対象Form/Entityと**同じパッケージ**
- クラス名は `<Form/Entityクラス名>Test`
- `nablarch.test.core.db.EntityTestSupport` を**継承**

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    // テスト対象クラス
    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // 文字種・文字列長の単項目精査テスト
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
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

---

#### テストデータの準備方法

テストデータはExcelファイルに記述し、**テストクラスと同じディレクトリに同じ名前**（拡張子のみ `.xlsx`）で配置する。

例: `UserRegistrationFormTest.java` → `UserRegistrationFormTest.xlsx`

Excelには以下のシートを作成する（各テスト種別で1シート使用）：

**文字種・文字列長の単項目精査シート（`testValidateCharsetAndLength` 用）**

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 許容する最小/最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenInvalidLength` | 文字列長不適合時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字` / `半角数字` / `全角カタカナ` / ... | 各文字種を許容するか（`o` = 許容、`x` = 不許容） |

このシートを用いると、以下のテストが自動実行される：
- 各文字種（半角英字/数字/記号/カナ、全角英字/数字/ひらがな/カタカナ/漢字/記号/外字）の入力テスト
- 未入力（空文字）テスト
- 最小文字列長・最大文字列長・超過・不足のテスト

---

#### コンポーネント設定ファイルの準備

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を設定する。Bean Validation使用時は `validationTestStrategy` に `BeanValidationTestStrategy` を**固定で**指定する。

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

**注意点**:
- プロパティとして別のFormを保持するFormには `testValidateCharsetAndLength` / `testSingleValidation` は使用不可。その場合は独自に精査処理のテストを実装する。
- Entityは自動生成されるため不要なsetter/getterが生成される可能性があり、Entity単体テストでは必ずsetter/getterのテストを実施すること。

参照:
- Bean Validationに対応したForm/Entityのクラス単体テスト
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md
  テストクラスの作成
  テストデータの作成
  文字種と文字列長の単項目精査テストケース
  テストケース表の作成方法
  テストメソッドの作成方法
  自動テストフレームワーク設定値
  設定項目一覧
  コンポーネント設定ファイルの記述例