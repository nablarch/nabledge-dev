**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルに記述する形で実施する。

## テストクラスの作り方

以下の3条件を満たすテストクラスを作成する。

1. テスト対象のFormと**同じパッケージ**にする
2. クラス名は `<Formクラス名>Test` とする
3. `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }

    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

## テストデータの準備方法

テストデータはExcelファイルで管理する。

- **場所**: テストクラスと同じディレクトリ
- **ファイル名**: テストクラスと同じ名前（拡張子のみ `.xlsx`）

Excelの各シートに用途別のテストデータを記述する。

### 文字種・文字列長の精査テスト用カラム

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小・最大文字列長 |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `半角数字`, `全角カタカナ`, ... | 各文字種を許容するか（`o` / `x`） |

### 事前設定（コンポーネント設定ファイル）

Bean Validation使用時は `BeanValidationTestStrategy` を指定する。

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
- 別のFormを保持するForm（`<親Form>.<子Form>.<プロパティ>` 形式）には `testValidateCharsetAndLength` / `testSingleValidation` が使用不可。独自実装が必要
- `testSetterAndGetter` の対象型には制限あり（String、BigDecimal、java.util.Date、`valueOf(String)` メソッドを持つクラス等）。`List<String>` など対象外の型は個別にテストを実装する
- メッセージデータやコードマスタなどの静的マスタデータは個別のテストデータとして作成しない

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json#s1`, `#s2`, `#s3`, `#s5`, `#s6`, `#s15`, `#s16`, `#s17`