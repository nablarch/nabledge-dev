**結論**: Bean Validation対応のFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータはExcelファイルに記述する。テストケースの種類（文字種・文字列長、その他単項目精査、項目間精査、setter/getter）ごとにシートを分け、対応するスーパークラスのメソッドを呼び出す。

**根拠**:

### テストクラスの作り方

以下の条件を満たすテストクラスを作成する（`testing-framework-01-entityUnitTestWithBeanValidation.json:s3`）:

- テスト対象のFormと**同じパッケージ**
- `<FormクラスName>Test` というクラス名
- `nablarch.test.core.db.EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }
}
```

### テストデータの準備方法

Excelファイルをテストソースコードと**同じディレクトリ**に**同じ名前（拡張子のみ `.xlsx`）**で配置する（`s2`）。セル書式はすべて文字列に設定すること（`testing-framework-01-Abstract.json:s14`）。

**シート構成（テストケース種別ごとに1シート）**:

**① 文字種・文字列長の単項目精査** (`s5`)

| カラム名 | 内容 |
|---|---|
| `propertyName` | プロパティ名 |
| `allowEmpty` | 未入力を許容するか（`o`/`x`） |
| `group` | Bean Validationのグループ（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenInvalidLength` | 文字列長不適合時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `半角数字`, `半角記号`, `半角カナ`, `全角英字`, `全角数字`, `全角ひらがな`, `全角カタカナ`, `全角漢字`, `全角記号その他`, `外字` | 各文字種を許容するか（`o`/`x`） |

**② その他の単項目精査（日付フォーマットなど）** (`s8`)

| カラム名 | 内容 |
|---|---|
| `propertyName` | プロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待メッセージ（エラーなしなら空欄） |

**③ 項目間精査（`@AssertTrue` など）** (`s11`)

1シートに2つのテーブルを作成する:
- **テストケース表**（ID: `testShots` 固定）: `title`, `description`, `group`, `expectedMessageId`n, `propertyName`n などのカラム
- **入力パラメータ表**（ID: `params` 固定）: 各プロパティの入力値を1行ずつ記述

### フレームワーク設定（初回のみ）

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する（`s16`, `s17`）:

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
    <!-- Bean Validationを使う場合は必ずBeanValidationTestStrategyを指定する -->
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
</component>
```

**注意点**:
- FormのプロパティはすべてString型として定義すること（`libraries-bean-validation.json:s8`）
- 別のFormをプロパティに持つ（ネストした）Formには `testValidateCharsetAndLength` / `testSingleValidation` が使えないため、独自にテストを実装すること（`s4`, `s7`）
- Entityは自動生成されるためsetter/getterのクラス単体テストが必須。一般的なFormはリクエスト単体テストでカバーできるため省略可能（`s13`）

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s7, s8, s9, s11, s12, s13, s16, s17 / libraries-bean-validation.json:s8 / testing-framework-01-Abstract.json:s14

---