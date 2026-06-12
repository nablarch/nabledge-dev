Step 4: セクション内容を読み込みました。回答を生成します。

---

**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルに外部化して実施する。テストの種類（文字種・文字列長、その他単項目精査、項目間精査、setter/getter）ごとに専用メソッドが用意されている。

---

**根拠**:

### テストクラスの作成

以下の条件でテストクラスを作成する。

- パッケージはテスト対象Formと同じ
- クラス名は `<Form名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // テストメソッドは以降のパターンに応じて追加
}
```

---

### テストデータ（Excelファイル）の準備

Excelファイルはテストソースコードと **同じディレクトリ** に **同じ名前**（拡張子のみ `.xlsx`）で配置する。

例：
| ファイル種別 | ファイル名 |
|---|---|
| テストソースコード | `UserRegistrationFormTest.java` |
| Excelファイル | `UserRegistrationFormTest.xlsx` |
| テスト対象クラス | `UserRegistrationForm.java` |

セルの書式は **すべて文字列形式** に設定すること。

---

### テストパターン 1: 文字種・文字列長の単項目精査

最も多くのケースをカバーする専用テスト方法。Excelシートに以下のカラムを用意する。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力許容か |
| `min` / `max` | 最小・最大文字列長 |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o`/`x`） |

テストメソッド:
```java
@Test
public void testCharsetAndLength() {
    String sheetName = "testCharsetAndLength";
    String id = "charsetAndLength";
    testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
}
```

---

### テストパターン 2: その他の単項目精査（日付フォーマット等）

任意の入力値と期待メッセージIDのペアを1行ずつ記述する。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージ（エラーなしの場合は空欄） |

テストメソッド:
```java
@Test
public void testSingleValidation() {
    String sheetName = "testSingleValidation";
    String id = "singleValidation";
    testSingleValidation(TARGET_CLASS, sheetName, id);
}
```

---

### テストパターン 3: 項目間精査（`@AssertTrue` 等）

テストケース表（ID: `testShots` 固定）と入力パラメータ表（ID: `params` 固定）の2つをExcelに定義する。

テストメソッド:
```java
@Test
public void testWholeFormValidation() {
    String sheetName = "testWholeFormValidation";
    testBeanValidation(TARGET_CLASS, sheetName);
}
```

---

### テストパターン 4: setter/getter

```java
@Test
public void testSetterAndGetter() {
    String sheetName = "testSetterAndGetter";
    String id = "setterAndGetter";
    testSetterAndGetter(TARGET_CLASS, sheetName, id);
}
```

---

### 必要なコンポーネント設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する（Bean Validationの場合は `BeanValidationTestStrategy` を指定）。

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
- Excelセルの書式は必ず **文字列形式** に設定する。数値・日付形式のままだと正しく読み取れない。
- `testSetterAndGetter` でテスト可能な型には制限がある（`String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラス等）。それ以外の型（例: `List<String>`）は個別にテストコードを書く必要がある。
- プロパティとして別のFormを保持するForm（親Form）には `testValidateCharsetAndLength` / `testSingleValidation` は使用できない。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, s2, s5, s6, s8, s9, s11, s12, s14, s16, s17 / testing-framework-01-Abstract.json:s9

---