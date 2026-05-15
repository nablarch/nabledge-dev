**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを定義して、フレームワーク提供のメソッドを呼び出す形で実装します。

**根拠**:

### テストクラスの作り方

以下の3条件を満たすテストクラスを作成します。

- パッケージは、テスト対象のForm/Entityと**同じ**にする
- クラス名は `<FormクラスName>Test` とする
- `nablarch.test.core.db.EntityTestSupport` を**継承**する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;
}
```

### テストデータの準備方法

Excelファイルをテストソースコードと**同じディレクトリ**に、**同じ名前**（拡張子のみ `.xlsx`）で配置します。

テストの種類に応じて、以下のシートを用意します（1テスト種別 = 1シート）。

#### (1) 文字種・文字列長の単項目精査テスト

Excelシートに以下のカラムを定義します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小/最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o`/`x`） |

テストメソッドはスーパークラスの `testValidateCharsetAndLength` を呼び出します。

```java
@Test
public void testCharsetAndLength() {
    String sheetName = "testCharsetAndLength";
    String id = "charsetAndLength";
    testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
}
```

#### (2) その他の単項目精査テスト（日付フォーマットなど）

任意の入力値と期待メッセージIDのペアをExcelに定義します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | プロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージID（エラーなしの場合は空欄） |

テストメソッドは `testSingleValidation` を呼び出します。

```java
@Test
public void testSingleValidation() {
    String sheetName = "testSingleValidation";
    String id = "singleValidation";
    testSingleValidation(TARGET_CLASS, sheetName, id);
}
```

#### (3) 項目間精査テスト（`@AssertTrue`など）

Excelに `testShots`（IDは固定）という表と `params` という入力パラメータ表の2つを定義します。

テストメソッドは `testBeanValidation` を呼び出します。

```java
@Test
public void testWholeFormValidation() {
    String sheetName = "testWholeFormValidation";
    testBeanValidation(TARGET_CLASS, sheetName);
}
```

### フレームワーク設定（必須）

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義し、Bean Validation使用時は `validationTestStrategy` に `BeanValidationTestStrategy` を**固定で**指定する必要があります。

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

- プロパティとして別のFormを保持する親Form（`<親Form>.<子Form>.<プロパティ名>` の形式）には、文字種/文字列長の単項目精査テスト方法は**使用できない**。その場合は独自に精査処理のテストを実装する
- `testSetterAndGetter` でテスト可能なプロパティ型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` を持つクラスなど限定的。`List<String>` のような型は個別に実装が必要
- メッセージIDをExcelに記載する際、`{}` で囲むとメッセージIDとして解決される（例: `{nablarch.core.validation.ee.Required.message}`）
- 静的マスタデータ（メッセージデータ、コードマスタ等）はプロジェクトで管理されたデータがあらかじめ投入されている前提で、個別のテストデータとして作成しない

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json#s3`, `#s2`, `#s5`, `#s6`, `#s8`, `#s9`, `#s16`, `#s17`