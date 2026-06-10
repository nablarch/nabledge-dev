**結論**: Bean ValidationのFormクラスの単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを記述する方式で行う。テスト種別（文字種/単項目精査/項目間精査/setter-getter）ごとにスーパークラスのメソッドを呼び出す。

---

**根拠**:

### テストクラスの作成

以下の3条件を満たすように作成する。

- パッケージはテスト対象のForm/Entityと同じにする
- クラス名は `<Form/Entityクラス名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // パッケージはUserRegistrationFormと同じ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    // クラス名はUserRegistrationFormTestで、EntityTestSupportを継承する
    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;
}
```

### テストデータの作成

テストデータを記載したExcelファイルは、テストソースコードと同じディレクトリに同じ名前で格納する（拡張子のみ異なる）。メッセージデータやコードマスタなどの静的マスタデータは、プロジェクトで管理されたデータがあらかじめ投入されている前提であり、個別のテストデータとして作成しない。

### テスト種別と対応メソッド

**1. 文字種と文字列長の単項目精査**

Excelに以下のカラムを含むシートを作成し、`testValidateCharsetAndLength`を呼び出す：

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| allowEmpty | 未入力を許容するか |
| group | Bean Validationのグループ（省略可） |
| min / max | 最小・最大文字列長（省略可） |
| messageIdWhenEmptyInput | 未入力時のメッセージ（省略可） |
| messageIdWhenInvalidLength | 文字列長不適合時のメッセージ（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時のメッセージ |
| 半角英字〜外字 | 各文字種を許容するか（`o`/`x`） |

```java
@Test
public void testCharsetAndLength() {
    String sheetName = "testCharsetAndLength";
    String id = "charsetAndLength";
    testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
}
```

**2. その他の単項目精査**（日付フォーマット精査など）

Excelカラム: `propertyName`, `case`, `group`, `input1`, `messageId`（精査エラーにならない場合は空欄）

```java
@Test
public void testSingleValidation() {
    String sheetName = "testSingleValidation";
    String id = "singleValidation";
    testSingleValidation(TARGET_CLASS, sheetName, id);
}
```

**3. 項目間精査**（`@AssertTrue`等）

テストケース表と入力パラメータ表を同じシートに作成し、`testBeanValidation`を呼び出す：

```java
@Test
public void testWholeFormValidation() {
    String sheetName = "testWholeFormValidation";
    testBeanValidation(TARGET_CLASS, sheetName);
}
```

**4. setter/getterのテスト**

```java
@Test
public void testSetterAndGetter() {
    String sheetName = "testSetterAndGetter";
    String id = "setterAndGetter";
    testSetterAndGetter(TARGET_CLASS, sheetName, id);
}
```

### フレームワーク設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する。Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を指定する（必須）：

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

---

**注意点**:
- `testSetterAndGetter`がサポートするプロパティ型はString、BigDecimal、java.util.Date、およびvalueOf(String)メソッドを持つクラス（Integer、Long、java.sql.Date等）に限定される。それ以外の型（例：`List<String>`）は個別にsetterとgetterを呼び出してテストする必要がある。
- 一般的なFormについては、リクエスト単体テストでsetter/getterのテストが可能なため、クラス単体テストでsetter/getterのテストを行う必要はない（Entityの場合は必須）。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s5, s6, s8, s9, s12, s14, s16, s17

---