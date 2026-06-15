**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを定義することで実施します。文字種・文字列長の単項目精査は`testValidateCharsetAndLength`、その他の精査は`testSingleValidation`メソッドを使用します。

**根拠**:

#### テストクラスの作成

以下の3つの条件を満たすテストクラスを作成します。

1. テストクラスのパッケージは、テスト対象のFormと**同じパッケージ**にする
2. クラス名は `<Formクラス名>Test` とする
3. `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // Formと同じパッケージ

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

    /** 単項目精査のテストケース（上記以外） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }
}
```

#### テストデータの準備（Excelファイル）

Excelファイルは**テストソースコードと同じディレクトリに、同じ名前（拡張子のみ異なる）**で格納します。

**① 文字種・文字列長テスト用シート（`testCharsetAndLength`）**

以下のカラムを持つテストケース表を定義します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` | 最小文字列長（省略可） |
| `max` | 最大文字列長（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時に期待するメッセージ |
| `半角英字` / `半角数字` / `全角カタカナ` など | 許容するか（`o` = 許容 / `x` = 不許容） |

このテストにより、文字種ごとの精査、最大・最小文字列長、未入力チェックが自動的に実行されます。

**② その他の単項目精査用シート（`testSingleValidation`）**

日付フォーマット精査など、文字種・文字列長以外の精査に使用します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージ（エラーなしの場合は空欄） |

#### コンポーネント設定ファイルの設定

テスト用コンポーネント設定ファイルに以下を追加します（Bean Validation使用時は `BeanValidationTestStrategy` の指定が必須）。

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
- メッセージデータやコードマスタなどの静的マスタデータは、プロジェクトで管理されたデータがあらかじめDBに投入されている前提です（個別のテストデータとして作成しません）。
- 子Formを`プロパティ`として保持する親Formには、`testValidateCharsetAndLength` / `testSingleValidation` は使用できません。その場合は独自に精査処理のテストを実装してください。
- `testSetterAndGetter`でテスト可能な型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` を持つクラスなどに限られます。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s4, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s7, testing-framework-01-entityUnitTestWithBeanValidation.json:s8, testing-framework-01-entityUnitTestWithBeanValidation.json:s9, testing-framework-01-entityUnitTestWithBeanValidation.json:s16