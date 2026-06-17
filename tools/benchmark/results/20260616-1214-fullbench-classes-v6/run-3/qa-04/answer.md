**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルで定義する方式で実装する。

**根拠**:

## テストクラスの作り方

以下の条件を満たすテストクラスを作成する。

- テストクラスのパッケージは、テスト対象のForm/Entityと**同じ**にする
- クラス名は `<FormクラスName>Test` とする
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
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査テスト（日付フォーマット等） */
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

スーパクラスが提供する主なメソッド:

| メソッド | 用途 |
|---|---|
| `testValidateCharsetAndLength(class, sheet, id)` | 文字種・文字列長の単項目精査 |
| `testSingleValidation(class, sheet, id)` | その他の単項目精査（任意の入力値とメッセージIDのペアで指定） |
| `testBeanValidation(class, sheet)` | 項目間精査（`@AssertTrue`等） |
| `testSetterAndGetter(class, sheet, id)` | setter/getterの検証 |

## テストデータの準備方法

テストデータはExcelファイルで定義する。**テストクラスと同じディレクトリに同じ名前（拡張子だけ異なる）**で配置する。

### 文字種・文字列長テスト用シート（`testCharsetAndLength`）

Excelに以下のカラムを持つ表を作成する:

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字` / `全角カタカナ` 等 | 各文字種を許容するか（`o` = 許容 / `x` = 不許容） |

フレームワークがこの表から自動的に、最大・最小文字列長の境界値、全文字種の許容/不許容を網羅するテストケースを生成して実行する。

### テスト用コンポーネント設定（必須）

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する:

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

Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定する。

**注意点**:
- Formのプロパティ型は**全て `String`** にすること（Bean Validationは入力値をBeanに変換した後でバリデーションするため、`String`以外にすると変換失敗で障害になる）
- メッセージデータやコードマスタ等の静的マスタデータはプロジェクト共通データとしてあらかじめ投入されている前提で、個別にExcelへ定義しない
- `@AssertTrue`を使った項目間精査は `testBeanValidation` メソッドで対応するが、別シートでの定義が必要

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s7, s9, s10, s12, s16, s17 / libraries-bean-validation.json:s8