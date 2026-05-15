**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスと、Excelファイルのテストデータを組み合わせて作成します。

---

**テストクラスの作り方**

以下の3条件を満たすテストクラスを作成します。

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {
    // クラス名: <FormクラS名>Test
    // EntityTestSupport を継承

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査テスト */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査テスト（@AssertTrue など） */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }

    /** setter/getter テスト */
    @Test
    public void testSetterAndGetter() {
        testSetterAndGetter(TARGET_CLASS, "testSetterAndGetter", "setterAndGetter");
    }
}
```

---

**テストデータの準備方法**

テストデータはExcelファイルで作成し、**テストソースコードと同じディレクトリに同じファイル名（拡張子のみ `.xlsx`）** で配置します。

**① 文字種・文字列長の単項目精査（`testValidateCharsetAndLength` 用）**

Excelシートに以下のカラムを定義します：

| propertyName | allowEmpty | min | max | messageIdWhenNotApplicable | 半角英字 | 半角数字 | 全角カタカナ | … |
|---|---|---|---|---|---|---|---|---|
| furigana | false | 1 | 50 | {nablarch...message} | x | x | o | … |

- `o` = 許容する、`x` = 許容しない
- `allowEmpty` が `false` の場合、空文字で精査エラーになることも自動テストされます

**② その他の単項目精査（`testSingleValidation` 用）**

| propertyName | case | input1 | messageId |
|---|---|---|---|
| birthDate | 不正な日付形式 | 20231399 | {date.format.message} |
| birthDate | 正常な日付 | 20231201 | （空欄） |

**③ 項目間精査（`testBeanValidation` 用）**

- IDが `testShots` 固定のテストケース表と、IDが `params` 固定の入力パラメータ表を同シートに用意します
- 例：パスワードとパスワード確認が一致するかを検証する `validPassword` プロパティのテスト

**④ コンポーネント設定ファイル（テスト用）**

Bean Validationを使う場合、`validationTestStrategy` に `BeanValidationTestStrategy` を指定します：

```xml
<component name="entityTestConfiguration" class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId" value="{nablarch.core.validation.ee.Length.max.message}"/>
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

**注意点**

- **ネストしたFormには使用不可**: `親Form.子Form.プロパティ名` でアクセスするネスト構造のFormに対しては `testValidateCharsetAndLength` / `testSingleValidation` は使用できません。その場合は独自に精査テストを実装してください。
- **setter/getterの対象型**: `testSetterAndGetter` でサポートされる型は `String`、`BigDecimal`、`java.util.Date`、および `valueOf(String)` を持つクラスのみです。`List<String>` など非対応型はテストコードで明示的に呼び出してください。
- **静的マスタデータ**: メッセージデータやコードマスタはプロジェクト共通データとしてあらかじめDBに投入されている前提のため、個別のテストデータとして作成しません。

参照: development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.json#s1, #s2, #s3, #s5, #s6, #s8, #s9, #s16, #s17