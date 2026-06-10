**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルで準備することで、文字種・文字列長・単項目精査・項目間精査を網羅的にテストできます。

---

**根拠**:

#### テストクラスの作り方

以下の条件を満たすテストクラスを作成します。

- パッケージはテスト対象のFormと同じにする
- クラス名は `<FormクラスName>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査 */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** その他の単項目精査（日付フォーマット等） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査 */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }
}
```

#### テストデータの準備方法

Excelファイルはテストクラス（`.java`）と**同じディレクトリに同じファイル名**で格納します（拡張子のみ `.xlsx`）。

**文字種・文字列長のテストケース表（1シート）**

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `group` | Bean ValidationのグループFQCN（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時に期待するメッセージID（省略可） |
| `messageIdWhenInvalidLength` | 文字列長不適合時のメッセージID（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時のメッセージID |
| `半角英字` 〜 `外字` | 各文字種を許容するか（`o` / `x`） |

例: フリガナ（最大50文字・必須・全角カタカナのみ）の場合、以下のケースが自動生成されます。

| テストケース | 観点 |
|---|---|
| 全角カタカナ50文字 → 精査成功 | 最大文字列長・文字種の確認 |
| 全角カタカナ51文字 → 精査失敗 | 最大文字列長の確認 |
| 空文字 → 精査失敗 | 必須精査の確認 |
| 半角カタカナ → 精査失敗 | 文字種の確認 |

**その他の単項目精査テストケース表**（日付フォーマット等）

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値（複数パラメータは `input2`, `input3` と増やす） |
| `messageId` | 期待するメッセージID（精査エラーなしは空欄） |

**項目間精査テストケース表**（`@AssertTrue` 等）

- テストケース表のIDは `"testShots"` 固定
- 入力パラメータ表のIDは `"params"` 固定

#### フレームワーク設定（コンポーネント設定ファイル）

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
- このテスト方法は、プロパティとして別のFormを保持するForm（`親Form.子Form.プロパティ名` 形式）には使用できません。その場合は独自に実装してください。
- Formクラスの場合、setter/getterのテストはリクエスト単体テストで代替できるため、クラス単体テストでの実施は不要です（Entityは自動生成されるため必須）。
- メッセージデータやコードマスタ等の静的マスタはプロジェクト管理データが投入済みの前提で、個別テストデータとして作成しません。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s7, s8, s9, s11, s12, s15

---