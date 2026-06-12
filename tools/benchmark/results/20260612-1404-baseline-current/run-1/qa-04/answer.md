**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルで準備する。テストクラス名は`<Form名>Test`とし、テストソースコードと同じディレクトリに同名のExcelファイル（拡張子のみ`.xlsx`）を配置する。

**根拠**:

### テストクラスの作成

以下の条件を満たすテストクラスを作成する。

- テストクラスのパッケージは、テスト対象のForm/Entityと同じにする
- クラス名は `<Form/Entityクラス名>Test` にする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

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

    /** その他の単項目精査（日付フォーマットなど） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査（@AssertTrueなど） */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    /** setter/getterのテスト */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

### テストデータの準備（Excelファイル）

Excelファイルはテストクラスと同じディレクトリに、同じ名前（拡張子`.xlsx`）で配置する。テストの種類ごとにシートを分けて記述する。

**①文字種・文字列長の単項目精査シート（`testCharsetAndLength`）**

各プロパティについて以下のカラムを用意する:

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象プロパティ名 |
| allowEmpty | 未入力を許容するか |
| min / max | 最小・最大文字列長（省略可） |
| messageIdWhenEmptyInput | 未入力時のメッセージ（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時のメッセージ |
| 半角英字〜外字 | 各文字種を許容するか（`o`=許容 / `x`=不可） |

`testValidateCharsetAndLength`を呼び出すことで、文字種ごとの精査・最長最短文字列・文字列長超過/不足の全観点が自動テストされる。

**②その他の単項目精査シート（`testSingleValidation`）**

日付フォーマットなど、①でカバーできない精査用。各プロパティに入力値と期待メッセージIDのペアを記述する。

**③項目間精査シート（`testWholeFormValidation`）**

`@AssertTrue`などによる項目間精査用。IDは`testShots`（テストケース表）と`params`（入力パラメータ表）固定。

### コンポーネント設定ファイル（test用）

`EntityTestConfiguration`をテスト用コンポーネント設定ファイルに追加する:

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
- メッセージデータやコードマスタなどの静的マスタデータは個別のテストデータとして作成せず、プロジェクトで管理されたデータがあらかじめDBに投入されている前提となる
- プロパティとして別のFormを保持する親Form（`<親Form>.<子Form>.<プロパティ名>`形式でアクセス）に対しては、`testValidateCharsetAndLength`/`testSingleValidation`は使用できないため、独自に実装する必要がある
- `testSetterAndGetter`でテスト可能な型は`String`、`BigDecimal`、`java.util.Date`、`valueOf(String)`を持つクラスなどに限られる。`List<String>`などはgetParamMapを用いた個別実装が必要

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s16, s17