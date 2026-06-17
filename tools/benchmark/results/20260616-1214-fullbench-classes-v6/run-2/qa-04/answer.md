**結論**: Bean ValidationのFormクラス単体テストは、`nablarch.test.core.db.EntityTestSupport` を継承したテストクラスを作成し、テストデータをExcelファイルで管理することで実装する。

**根拠**:

### テストクラスの作り方

以下の3条件を満たすテストクラスを作成する。

1. パッケージはテスト対象のFormと同じにする
2. クラス名は `<Formクラス名>Test` にする
3. `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form;  // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長の単項目精査 */
    @Test
    public void testCharsetAndLength() {
        testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
    }

    /** その他の単項目精査（日付フォーマット等） */
    @Test
    public void testSingleValidation() {
        testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
    }

    /** 項目間精査（@AssertTrue 等） */
    @Test
    public void testWholeFormValidation() {
        testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
    }
}
```

JUnit 5 を使う場合は `@EntityTest` アノテーションと `EntityTestSupport` のフィールドインジェクションで代替できる。

### テストデータの準備方法

テストデータはExcelファイルで管理する。**テストソースコードと同じディレクトリに、同じファイル名（拡張子のみ `.xlsx`）で格納する。**

テストの種類に応じてシートを分けて記述する。

**① 文字種・文字列長テスト用シート**（`testValidateCharsetAndLength` で使用）

以下のカラムを持つテーブルを作成する。

| カラム名 | 記載内容 |
|---|---|
| propertyName | テスト対象プロパティ名 |
| allowEmpty | 未入力許容の有無 |
| min / max | 最小・最大文字列長（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時のメッセージ |
| 半角英字〜外字 | 各文字種を許容するか（`o` / `x`） |

このシートを読み込むと、各文字種での合否・境界値テストが自動実行される。

**② 項目間精査テスト用シート**（`testBeanValidation` で使用）

- IDが `testShots` のテストケース表（title / expectedMessageId_n / propertyName_n 等）
- IDが `params` の入力パラメータ表

を1シートにまとめて記述する。

### コンポーネント設定ファイルへの追加

Bean Validationを使う場合は、テスト用コンポーネント設定ファイルに以下を追加する（`validationTestStrategy` に `BeanValidationTestStrategy` を指定するのが必須）。

```xml
<component name="entityTestConfiguration"
           class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"
            value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="maxAndMinMessageId"
            value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="fixLengthMessageId"
            value="{nablarch.core.validation.ee.Length.fixed.message}"/>
  <property name="underLimitMessageId"
            value="{nablarch.core.validation.ee.Length.min.max.message}"/>
  <property name="minMessageId"
            value="{nablarch.core.validation.ee.Length.min.message}"/>
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

参照: testing-framework-01-entityUnitTestWithBeanValidation.json:s2, testing-framework-01-entityUnitTestWithBeanValidation.json:s3, testing-framework-01-entityUnitTestWithBeanValidation.json:s4, testing-framework-01-entityUnitTestWithBeanValidation.json:s5, testing-framework-01-entityUnitTestWithBeanValidation.json:s6, testing-framework-01-entityUnitTestWithBeanValidation.json:s7, testing-framework-01-entityUnitTestWithBeanValidation.json:s9, testing-framework-01-entityUnitTestWithBeanValidation.json:s12, testing-framework-01-entityUnitTestWithBeanValidation.json:s16, testing-framework-01-entityUnitTestWithBeanValidation.json:s17