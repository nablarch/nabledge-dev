**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイル（テストクラスと同名・同ディレクトリ）に記述して3種類のテストメソッドで実行します。

---

**根拠**:

#### テストクラスの作り方

以下の条件でテストクラスを作成します。

- パッケージはテスト対象のFormと同じにする
- クラス名は `<Formクラス名>Test` にする
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

    /** その他の単項目精査 */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }

    /** 項目間精査（@AssertTrue等） */
    @Test
    public void testWholeFormValidation() {
        String sheetName = "testWholeFormValidation";
        testBeanValidation(TARGET_CLASS, sheetName);
    }
}
```

#### テストデータの準備方法

**Excelファイルの配置**: テストソースコードと同じディレクトリに同じ名前（拡張子のみ `.xlsx`）で配置します。

**① 文字種・文字列長の単項目精査（`testValidateCharsetAndLength`）**

以下のカラムを持つテストケース表をExcelシートに作成します。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 許容する最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `全角カタカナ` 等 | 許容するか（`o`/`x` で記入） |

**② その他の単項目精査（`testSingleValidation`）**

日付フォーマット等、上記でカバーできない精査に使います。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージID（精査エラーなしの場合は空欄） |

**③ 項目間精査（`testBeanValidation`）**

`@AssertTrue` を指定した精査など複数プロパティをまたぐテストに使います。

- ID `"testShots"` 固定のテストケース表（`title`, `expectedMessageId1`, `propertyName1` 等）
- ID `"params"` 固定の入力パラメータ表（各テストケースへの入力値）

#### 必要な設定（コンポーネント設定ファイル）

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"
            value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="emptyInputMessageId"
            value="{nablarch.core.validation.ee.Required.message}"/>
  <property name="validationTestStrategy">
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
  <!-- 他のmessageIdプロパティも設定 -->
</component>
```

---

**注意点**:
- Excelのセルの書式は**文字列**のみ対応です。数値書式のセルは読み込めません。
- プロパティとして別のFormを保持するFormには、`testValidateCharsetAndLength` および `testSingleValidation` は使用できません。その場合は独自にテストを実装してください。
- 一般的なFormのsetter/getterテストは、リクエスト単体テストで行えるため、クラス単体テストでは省略可能です（Entityの場合は必須）。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s8, testing-framework-01-entityUnitTestWithBeanValidation.json:s9, testing-framework-01-entityUnitTestWithBeanValidation.json:s11, testing-framework-01-entityUnitTestWithBeanValidation.json:s12, testing-framework-01-entityUnitTestWithBeanValidation.json:s13, testing-framework-01-entityUnitTestWithBeanValidation.json:s17, testing-framework-01-Abstract.json:s9

---