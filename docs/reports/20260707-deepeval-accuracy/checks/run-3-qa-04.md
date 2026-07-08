# qa-04 — run-3

## 質問

Bean ValidationのFormクラスの単体テストを書きたい。テストクラスの作り方とテストデータの準備方法を教えてほしい

## 回答

**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルで定義する方式で実装する。

**根拠**:

## テストクラスの作り方

以下の条件を満たすテストクラスを作成する。

- テストクラスのパッケージは、テスト対象のForm/Entityと**同じ**にする
- クラス名は `<FormクラスName>Test` とする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査テスト（日付フォーマット等） */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査テスト（@AssertTrue等） */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }

    /** setter/getterテスト */
    @Test
    public void testSetterAndGetter() {
        testSetterAndGetter(TARGET_CLASS, "testSetterAndGetter", "setterAndGetter");
    }
}
```

スーパクラスが提供する主なメソッド:

| メソッド | 用途 |
|---|---|
| `testValidateCharsetAndLength(class, sheet, id)` | 文字種・文字列長の単項目精査 |
| `testSingleValidation(class, sheet, id)` | その他の単項目精査（任意の入力値とメッセージIDのペアで指定） |
| `testBeanValidation(class, sheet)` | 項目間精査（`@AssertTrue`等） |
| `testSetterAndGetter(class, sheet, id)` | setter/getterの検証 |

## テストデータの準備方法

テストデータはExcelファイルで定義する。**テストクラスと同じディレクトリに同じ名前（拡張子だけ異なる）**で配置する。

### 文字種・文字列長テスト用シート（`testCharsetAndLength`）

Excelに以下のカラムを持つ表を作成する:

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字` / `全角カタカナ` 等 | 各文字種を許容するか（`o` = 許容 / `x` = 不許容） |

フレームワークがこの表から自動的に、最大・最小文字列長の境界値、全文字種の許容/不許容を網羅するテストケースを生成して実行する。

### テスト用コンポーネント設定（必須）

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を定義する:

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

Bean Validationを使う場合は `validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定する。

**注意点**:
- Formのプロパティ型は**全て `String`** にすること（Bean Validationは入力値をBeanに変換した後でバリデーションするため、`String`以外にすると変換失敗で障害になる）
- メッセージデータやコードマスタ等の静的マスタデータはプロジェクト共通データとしてあらかじめ投入されている前提で、個別にExcelへ定義しない
- `@AssertTrue`を使った項目間精査は `testBeanValidation` メソッドで対応するが、別シートでの定義が必要

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, s3, s4, s5, s6, s7, s9, s10, s12, s16, s17 / libraries-bean-validation.json:s8

## 参照ナレッジ

- [テストデータの作成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストデータの作成) (s2)
- [テストクラスの作成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストクラスの作成) (s3)
- [文字種と文字列長の単項目精査テストケース](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#文字種と文字列長の単項目精査テストケース) (s4)
- [テストケース表の作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストケース表の作成方法) (s5)
- [テストメソッドの作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストメソッドの作成方法) (s6)
- [その他の単項目精査のテストケース](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#その他の単項目精査のテストケース) (s7)
- [テストメソッドの作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストメソッドの作成方法) (s9)
- [項目間精査のテストケース](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#項目間精査のテストケース) (s10)
- [テストメソッドの作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#テストメソッドの作成方法) (s12)
- [setter、getterに対するテストケース](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#settergetterに対するテストケース) (s13)
- [自動テストフレームワーク設定値](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#自動テストフレームワーク設定値) (s15)
- [設定項目一覧](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#設定項目一覧) (s16)
- [コンポーネント設定ファイルの記述例](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md#コンポーネント設定ファイルの記述例) (s17)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers both expected facts: (1) it clearly states that the test class should inherit `EntityTestSupport` (nablarch.test.core.db.EntityTestSupport) with a code example showing the inheritance, and (2) it explicitly states that test data is defined in Excel files and placed in the same directory as the test class. Both facts from the Expected Output checklist are fully addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response perfectly addresses the question about writing unit tests for Bean Validation Form classes, covering both test class creation and test data preparation with no irrelevant statements. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「EntityTestSupportを継承してテストクラスを作成する」は回答の`public class UserRegistrationFormTest extends EntityTestSupport`（コード例）および「nablarch.test.core.db.EntityTestSupportを継承する」に含まれている。参照事実「テストデータはExcelファイルに記述する」は回答の「テストデータはExcelファイルで定義する」に含まれている。 |
| answer_relevancy | OK | 回答はテストクラスの作り方とテストデータの準備方法という質問の両部分に直接答えており、テストクラス構造・Excelデータ形式・コンポーネント設定のいずれも質問に対して必要な内容である。質問と無関係な情報は含まれていない。 |
| faithfulness | OK | 回答の主要な主張はすべてナレッジMDと一致している。テストクラスの3条件（同パッケージ・クラス名・EntityTestSupport継承）、4つのスーパークラスメソッド、Excelファイルの配置ルール（同ディレクトリ・同名・拡張子のみ異なる）、Excelカラム構成、XMLコンポーネント設定例、静的マスタデータを個別定義しない旨、BeanValidationTestStrategyを固定指定する旨、いずれもナレッジの記述と矛盾しない。 |

### 参照事実（expected_facts）

- EntityTestSupportを継承してテストクラスを作成する
- テストデータはExcelファイルに記述する
