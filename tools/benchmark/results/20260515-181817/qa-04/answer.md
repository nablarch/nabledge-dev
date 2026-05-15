**結論**: Bean ValidationのForm単体テストは、`EntityTestSupport`を継承したテストクラスとExcelファイルのテストデータをセットで作成します。

**根拠**:

## テストクラスの作成

以下3つの条件を満たすテストクラスを作成します。

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport { // クラス名はFormクラス名 + "Test"
    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // 文字種・文字列長の単項目精査テスト
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    // その他の単項目精査テスト（日付フォーマット等）
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    // 項目間精査テスト（@AssertTrue等）
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }

    // setter/getterテスト
    @Test
    public void testSetterAndGetter() {
        testSetterAndGetter(TARGET_CLASS, "testSetterAndGetter", "setterAndGetter");
    }
}
```

## テストデータ（Excel）の準備

テストソースコードと同じディレクトリに同じ名前（拡張子のみ`.xlsx`）で配置します。

**シート1: 文字種・文字列長テスト（`testCharsetAndLength`シート）**

| カラム | 内容 |
|--------|------|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `group` | Bean Validationのグループ（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`〜`外字` | 各文字種を許容するか（`o`/`x`） |

**シート2: 項目間精査テスト（`testWholeFormValidation`シート）**

- `testShots`表（IDは"testShots"固定）: `title`, `description`, `group`, `expectedMessageId1`, `propertyName1`等を記載
- `params`表（IDは"params"固定）: 各テストケースの入力パラメータを1行ずつ記載

## フレームワーク設定（コンポーネント設定ファイル）

```xml
<component name="entityTestConfiguration" class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"        value="{nablarch.core.validation.ee.Length.max.message}"/>
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
- `validationTestStrategy`には`BeanValidationTestStrategy`を必ず指定してください（Nablarchバリデーションと異なります）
- プロパティとして別のFormを保持する親Formには、この単項目精査テスト方式は使用できません。その場合は独自に実装してください
- 一般的なFormのsetter/getterテストはリクエスト単体テストで代替可能なため、クラス単体テストでは必須ではありません
- `testSetterAndGetter`でテスト可能な型は`String`、`BigDecimal`、`java.util.Date`、`valueOf(String)`を持つクラスに限定されます。`List<String>`等は個別に実装が必要です

参照: `development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.json#s3`, `#s2`, `#s5`, `#s6`, `#s8`, `#s9`, `#s11`, `#s12`, `#s14`, `#s16`, `#s17`