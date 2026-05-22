Step 5〜8: 回答を生成し、検証します。

---

**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルに記述して実行する。

**根拠**:

## テストクラスの作り方

以下の条件を満たすテストクラスを作成する。

- パッケージはテスト対象のFormクラスと同じにする
- クラス名は `<FormクラスName>Test` にする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // パッケージはFormと同じ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // テストメソッドは以降の説明を参照
}
```

## テストデータの準備方法

テストデータはExcelファイルに記述する。配置ルールは以下のとおり。

- **ファイル名**: テストクラスと同じ名前（拡張子のみ `.xlsx`）
- **配置場所**: テストソースコードと同じディレクトリ

メッセージデータやコードマスタなどの静的マスタデータは、プロジェクトで管理されたデータがあらかじめ投入されている前提であり、個別のテストデータとして作成しない。

## テストの種類と書き方

### ①文字種・文字列長の単項目精査（メインのテスト）

Excelシートに以下のカラムを用意し、`testValidateCharsetAndLength()` を呼び出す。

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時のメッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o` / `x`） |

```java
@Test
public void testCharsetAndLength() {
    String sheetName = "testCharsetAndLength";
    String id = "charsetAndLength";
    testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
}
```

### ②その他の単項目精査（日付フォーマット等）

文字種・文字列長でカバーできない精査（例：日付フォーマット）は、入力値と期待メッセージIDのペアをExcelに記述し、`testSingleValidation()` を呼び出す。

```java
@Test
public void testSingleValidation() {
    String sheetName = "testSingleValidation";
    String id = "singleValidation";
    testSingleValidation(TARGET_CLASS, sheetName, id);
}
```

### ③項目間精査（`@AssertTrue` 等）

`@AssertTrue` を使った相関バリデーションは、`testBeanValidation()` を使う。ExcelシートにIDは `testShots`（期待メッセージ）と `params`（入力パラメータ）の2つの表を記述する。

```java
@Test
public void testWholeFormValidation() {
    String sheetName = "testWholeFormValidation";
    testBeanValidation(TARGET_CLASS, sheetName);
}
```

## コンポーネント設定ファイルの設定

テスト用コンポーネント設定ファイルに、`EntityTestConfiguration` を定義する。Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を指定することが必須。

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

**注意点**: `testValidateCharsetAndLength()` はネストしたForm（子Formのプロパティを `parentForm.childForm.property` の形式でアクセスするForm）には使用できない。その場合は独自に精査処理のテストを実装すること。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, s2, s4, s5, s6, s7, s9, s12, s16, s17

---