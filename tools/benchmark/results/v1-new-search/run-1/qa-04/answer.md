セクション内容を確認しました。Step 5で回答を生成します。

**結論**: `EntityTestSupport` を継承したテストクラスを作成し、テストデータはExcelファイル（テストクラスと同じディレクトリ・同じファイル名）に記述します。テスト種別ごとに専用メソッド（`testValidateCharsetAndLength`、`testSingleValidation`、`testBeanValidation`）を呼び出します。

---

**根拠**:

### テストクラスの作り方

以下の条件を満たすテストクラスを作成します。

- パッケージ: テスト対象Formと同じ
- クラス名: `<Form名>Test`
- スーパークラス: `nablarch.test.core.db.EntityTestSupport`

```java
package com.nablarch.example.app.web.form;

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // 文字種・文字列長の単項目精査
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    // その他の単項目精査（日付フォーマット等）
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    // 項目間精査（@AssertTrue 等）
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }

    // setter/getter
    @Test
    public void testSetterAndGetter() {
        testSetterAndGetter(TARGET_CLASS, "testSetterAndGetter", "setterAndGetter");
    }
}
```

---

### テストデータの準備方法

Excelファイルをテストクラスと同じディレクトリに、同じ名前（拡張子 `.xlsx`）で格納します。

**1. 文字種・文字列長テスト用シート（`testCharsetAndLength`）**

以下のカラムを含むテストケース表（`LIST_MAP=charsetAndLength`）を作成します。

| カラム名 | 記載内容 |
|---------|---------|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力許容か（`o` / `x`） |
| `min` / `max` | 最小・最大文字列長 |
| `messageIdWhenEmptyInput` | 未入力時のメッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時のメッセージ |
| 半角英字、全角漢字 … 外字 | 各文字種を許容するか（`o` / `x`） |

**2. その他単項目精査テスト用シート（`testSingleValidation`）**

| カラム名 | 記載内容 |
|---------|---------|
| `propertyName` | プロパティ名 |
| `case` | ケース説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージ（エラーなし期待は空欄） |

**3. 項目間精査テスト用シート（`testWholeFormValidation`）**

- ID `testShots` のテストケース表（期待エラーメッセージとプロパティ名）
- ID `params` の入力パラメータ表（各ケースの入力値）

---

### 事前設定（コンポーネント設定ファイル）

Bean Validationを使う場合は `BeanValidationTestStrategy` を設定します。

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"
            value="{nablarch.core.validation.ee.Length.max.message}"/>
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

---

**注意点**:
- Excelのセル書式は**文字列**にしておくこと（数値書式だと読み取りが正しく行われない）
- `testSetterAndGetter` で扱えるプロパティ型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` を持つクラスに限定される。`List<String>` 等は個別テストが必要

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json:s2`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s3`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s5`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s6`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s8`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s16`, `testing-framework-01-entityUnitTestWithBeanValidation.json:s17`

---