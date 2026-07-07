# qa-04 — run-1

## 質問

Bean ValidationのFormクラスの単体テストを書きたい。テストクラスの作り方とテストデータの準備方法を教えてほしい

## 回答

**結論**: Bean Validation対応のForm/Entity単体テストは、`EntityTestSupport`を継承したテストクラスと、同一ディレクトリに配置したExcelファイルの組み合わせで作成する。

**根拠**:

### テストクラスの作成

以下の条件を満たすテストクラスを作成する。
- パッケージはテスト対象のFormと同じにする
- クラス名は `<Formクラス名>Test` にする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form;

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

### テストデータの準備

Excelファイルはテストクラスと**同じディレクトリに同じ名前**で格納する（拡張子のみ `.xlsx`）。例えば `UserRegistrationFormTest.java` に対して `UserRegistrationFormTest.xlsx` を作成する。

**文字種・文字列長テスト（testCharsetAndLength シート）の主なカラム:**

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| allowEmpty | 未入力を許容するか (o/x) |
| min / max | 最小・最大文字列長 |
| messageIdWhenNotApplicable | 文字種不適合時のメッセージ |
| 半角英字〜外字 | 各文字種を許容するか (o/x) |

### フレームワーク設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する。Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を必ず指定する。

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

**注意点**: `testValidateCharsetAndLength` はプロパティとして別のFormを保持するForm（親Form.子Form.プロパティ形式でアクセスするForm）には使用できない。その場合は独自に精査処理のテストを実装すること。

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s15, s16, s17

## 参照ナレッジ

- [テストデータの作成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストデータの作成) (s2)
- [テストクラスの作成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストクラスの作成) (s3)
- [文字種と文字列長の単項目精査テストケース](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#文字種と文字列長の単項目精査テストケース) (s4)
- [テストケース表の作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストケース表の作成方法) (s5)
- [テストメソッドの作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストメソッドの作成方法) (s6)
- [自動テストフレームワーク設定値](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#自動テストフレームワーク設定値) (s15)
- [設定項目一覧](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#設定項目一覧) (s16)
- [コンポーネント設定ファイルの記述例](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#コンポーネント設定ファイルの記述例) (s17)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers both expected facts: it explicitly mentions inheriting `EntityTestSupport` (with the full class path `nablarch.test.core.db.EntityTestSupport`) for the test class, and it explicitly states that test data should be written in an Excel file placed in the same directory with the same name as the test class. Both facts from the Expected Output checklist are fully present in the Actual Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to write unit tests for Bean Validation Form classes, including test class creation and test data preparation. Great job! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- EntityTestSupportを継承してテストクラスを作成する
- テストデータはExcelファイルに記述する
