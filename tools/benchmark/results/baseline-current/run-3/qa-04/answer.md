**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを定義する方式で実施します。

**根拠**:

### テストクラスの作成

以下の条件を満たすテストクラスを作成します。

- テストクラスのパッケージは、テスト対象のForm/Entityと**同じ**にする
- クラス名は `<Form名>Test` とする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** その他の単項目精査テスト */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査テスト */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    /** setter/getterテスト */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

### テストデータの準備方法

テストデータは **Excelファイル**（テストクラスと**同じディレクトリ・同じ名前**で `*.xlsx` 拡張子）に定義します。

#### 文字種・文字列長テスト（シート: `testCharsetAndLength`）

Excelシートに以下のカラムを用意します：

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `group` | Bean Validationグループ（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenInvalidLength` | 文字列長不適合時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o`=許容 / `x`=不許容） |

#### その他の単項目精査（シート: `testSingleValidation`）

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージ（エラーなしなら空欄） |

#### 項目間精査（シート: `testWholeFormValidation`）

- IDは `testShots` 固定のテストケース表と、IDは `params` 固定の入力パラメータ表の2つが必要

### フレームワーク設定（コンポーネント設定ファイル）

Bean Validationを使用する場合、テスト用コンポーネント設定ファイルに `validationTestStrategy` を `BeanValidationTestStrategy` で設定することが必須です：

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

**注意点**:
- プロパティとして別のFormを保持する「ネストForm」には、`testValidateCharsetAndLength` および `testSingleValidation` は使用できない。その場合は独自に精査テストを実装する必要がある
- `testSetterAndGetter` でテスト可能な型は `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)` メソッドを持つクラスに限定される。`List<String>` 等は個別実装が必要
- `setter/getter` に独自ロジックがある場合（例: 郵便番号上3桁+下4桁→7桁返却）は、そのロジックを検証するテストケースも追加すること

参照: `development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.json#s3`, `#s2`, `#s5`, `#s6`, `#s16`, `#s17`