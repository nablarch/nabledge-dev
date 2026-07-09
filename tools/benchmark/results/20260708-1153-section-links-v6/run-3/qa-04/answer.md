**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport`を継承したテストクラスを作成し、テストデータをExcelファイルに記述することで実装する。

---

**根拠**:

## テストクラスの作成

以下の条件を満たすテストクラスを作成する。

- テスト対象Formクラスと同じパッケージにクラスを作成する
- クラス名は `<FormクラスName>Test` とする
- `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種および文字列長の単項目精査テスト */
    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }

    /** その他の単項目精査テスト（日付フォーマットなど） */
    @Test
    public void testSingleValidation() {
        String sheetName = "testSingleValidation";
        String id = "singleValidation";
        testSingleValidation(TARGET_CLASS, sheetName, id);
    }
}
```

**JUnit 5を使う場合**: `@EntityTest` 合成アノテーションをクラスに付与し、`EntityTestSupport` 型のフィールドとしてインジェクションする方式を使う。

---

## テストデータの準備

Excelファイルを **テストソースコードと同じディレクトリに同じファイル名（拡張子のみ `.xlsx`）** で格納する（例: `UserRegistrationFormTest.xlsx`）。

### 文字種・文字列長の単項目精査テストケース表

Excelのシートに以下のカラムを用意する。

| カラム名 | 記載内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小/最大文字列長（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時に期待するメッセージ |
| `messageIdWhenEmptyInput` | 未入力時のメッセージ（省略可） |
| 半角英字〜外字の各カラム | 許容する場合は `o`、許容しない場合は `x` |

### コンポーネント設定ファイルへの設定

テスト用コンポーネント設定ファイルに `EntityTestConfiguration` を設定する。Bean Validationを使う場合、`validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定する。

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
- プロパティとして別のFormを保持するForm（`<親Form>.<子Form>.<プロパティ名>` 形式でアクセスする親Form）には本テスト方法は使用できない。その場合は独自に精査処理のテストを実装すること。
- メッセージデータやコードマスタなどの静的マスタデータはプロジェクトで管理されたデータが事前投入済みである前提のため、個別テストデータとして作成しない。

参照:
- Bean Validationに対応したForm/Entityのクラス単体テスト
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md
  Form/Entity単体テストの書き方
  テストデータの作成
  テストクラスの作成
  文字種と文字列長の単項目精査テストケース
  テストケース表の作成方法
  テストメソッドの作成方法
  その他の単項目精査のテストケース
  自動テストフレームワーク設定値
  設定項目一覧
  コンポーネント設定ファイルの記述例
- JUnit 5用拡張機能
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-JUnit5-Extension.md
  基本的な使い方
  Extension クラスと合成アノテーションの一覧