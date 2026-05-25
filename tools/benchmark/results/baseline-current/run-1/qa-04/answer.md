**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport` を継承したテストクラスを作成し、Excelファイルにテストデータを定義して実行します。

### テストクラスの作り方

以下の条件でテストクラスを作成します。

- パッケージ: テスト対象のForm/Entityと **同じパッケージ**
- クラス名: `<Form名>Test`
- スーパークラス: `nablarch.test.core.db.EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;
}
```

### テストデータの準備方法

Excelファイルをテストクラスと **同じディレクトリ・同じファイル名（拡張子のみ `.xlsx`）** で配置します。

#### ① 文字種・文字列長の単項目精査

シートに以下のカラムを定義し、`testValidateCharsetAndLength()` で実行します。

カラム: propertyName, allowEmpty, group, min, max, messageIdWhenEmptyInput, messageIdWhenInvalidLength, messageIdWhenNotApplicable, 半角英字〜外字（o/x）

```java
@Test
public void testCharsetAndLength() {
    testValidateCharsetAndLength(TARGET_CLASS, "testCharsetAndLength", "charsetAndLength");
}
```

#### ② その他の単項目精査（日付フォーマットなど）

カラム: propertyName, case, group, input1, messageId

```java
@Test
public void testSingleValidation() {
    testSingleValidation(TARGET_CLASS, "testSingleValidation", "singleValidation");
}
```

#### ③ 項目間精査（`@AssertTrue` など）

```java
@Test
public void testWholeFormValidation() {
    testBeanValidation(TARGET_CLASS, "testWholeFormValidation");
}
```

### フレームワーク設定（必須）

```xml
<component name="entityTestConfiguration" class="nablarch.test.core.entity.EntityTestConfiguration">
  <property name="maxMessageId"        value="{nablarch.core.validation.ee.Length.max.message}"/>
  <property name="emptyInputMessageId" value="{nablarch.core.validation.ee.Required.message}"/>
  <property name="validationTestStrategy">
    <component class="nablarch.test.core.entity.BeanValidationTestStrategy"/>
  </property>
</component>
```

**注意点**:
- `validationTestStrategy` に `BeanValidationTestStrategy` を固定で指定しないと Bean Validation が動作しません
- プロパティとして別のFormを保持するネストしたFormに対しては `testValidateCharsetAndLength()` は使用できません
- setter/getterのテストは、一般的なFormであればリクエスト単体テストでカバーできるため省略可能です
- 静的マスタデータは個別テストデータとして作成する必要はありません

参照: development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.json#s3, #s2, #s5, #s6, #s8, #s9, #s12, #s16, #s17