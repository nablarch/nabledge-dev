Step 5の回答を生成します。

---

**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport` を継承したテストクラスと、Excelファイルのテストデータを組み合わせて作成する。テストデータはExcelの各シートに定義し、スーパークラスのメソッドを呼び出すだけでテストが実行される。

---

**根拠**:

### テストクラスの作成

以下の3条件を満たすテストクラスを作成する。

- テスト対象のFormと **同じパッケージ** にする
- クラス名は **`<FormクラスName>Test`**
- **`nablarch.test.core.db.EntityTestSupport`** を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種および文字列長の単項目精査 */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査 */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査 (@AssertTrue等) */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }
}
```

---

### テストデータの準備

テストデータはExcelファイルで準備する。**テストクラスと同じディレクトリ・同じファイル名（拡張子のみ `.xlsx`）** で配置する。

#### ① 文字種・文字列長の単項目精査（`testValidateCharsetAndLength`）

Excelシートに以下のカラムを定義する。

| カラム名 | 記載内容 |
|---|---|
| propertyName | プロパティ名 |
| allowEmpty | 未入力を許容するか |
| min / max | 最小・最大文字列長（省略可） |
| messageIdWhenEmptyInput | 未入力時の期待メッセージ（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時の期待メッセージ |
| 半角英字, 半角数字, 半角記号, 半角カナ, 全角英字, 全角数字, 全角ひらがな, 全角カタカナ, 全角漢字, 全角記号その他, 外字 | `o`（許容）/ `x`（不許容） |

このメソッドは文字種・未入力・最小最大文字列長など、各行ごとに自動的に多数のテストケースを実行する。

#### ② その他の単項目精査（`testSingleValidation`）

日付フォーマットなど、①でカバーできない精査に使用する。

| カラム名 | 記載内容 |
|---|---|
| propertyName | プロパティ名 |
| case | テストケース説明 |
| input1 | 入力値 |
| messageId | 精査エラー時の期待メッセージ（エラーなしの場合は空欄） |

#### ③ 項目間精査（`testBeanValidation`）

`@AssertTrue` 等による相関バリデーションに使用する。同一シートに以下の2つの表を定義する。

- **testShots表**（ID固定: `testShots`）: title, description, expectedMessageId*n*, propertyName*n* 等
- **入力パラメータ表**（ID固定: `params`）: 各テストショットの入力値を1行ずつ記載

---

### 事前設定（コンポーネント設定ファイル）

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義し、**`BeanValidationTestStrategy`** を必ず指定する。

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
- メッセージデータやコードマスタ等の静的マスタはあらかじめプロジェクト共通データとして投入されている前提であり、テストデータには個別に記述しない。
- `testSetterAndGetter` でsetter/getterテストも行える（対応型: `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` を持つクラスなど）。

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json:s2`, `s3`, `s5`, `s6`, `s8`, `s11`, `s12`, `s16`, `s17`

---