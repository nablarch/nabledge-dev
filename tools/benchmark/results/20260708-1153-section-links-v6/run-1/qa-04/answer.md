**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport` を継承したテストクラスを作成し、テストデータはExcelファイルに記述する。

**根拠**:

## テストクラスの作成

以下の条件を満たすテストクラスを作成する。

- テスト対象のFormクラスと同じパッケージ
- クラス名は `<Formクラス名>Test`
- `nablarch.test.core.db.EntityTestSupport` を継承

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

**JUnit 5 を使う場合**: `EntityTestSupport` の継承の代わりに `@EntityTest` アノテーションを使用し、`EntityTestSupport` 型フィールドをインジェクションする。

## テストデータの準備

Excelファイルをテストソースコードと**同じディレクトリ**に**同じ名前**（拡張子のみ `.xlsx`）で配置する。

### 文字種・文字列長テスト（`testCharsetAndLength`）のExcelシート構成

以下のカラムを定義する（1行1プロパティ）。

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `min` / `max` | 最小/最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ |
| `messageIdWhenInvalidLength` | 文字列長不適合時の期待メッセージ |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字` / `半角数字` / ... / `外字` | 各文字種を許容するか（`o`/`x`） |

### その他の単項目精査（`testSingleValidation`）のExcelシート構成

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象プロパティ名 |
| `case` | テストケースの説明 |
| `input1` | 入力値 |
| `messageId` | 精査エラー時の期待メッセージ（正常時は空欄） |

### 項目間精査（`testBeanValidation`）のExcelシート構成

- テストケース表：ID = `testShots`（固定）。`expectedMessageId1`, `propertyName1` 等のカラムで期待エラーを定義
- 入力パラメータ表：ID = `params`（固定）。プロパティ値を1行1ケースで記述

**注意点**: プロパティとして別のFormを保持するFormには、`testValidateCharsetAndLength`/`testSingleValidation` は使用できない。その場合は個別にテストを実装する。

参照:
- Bean Validationに対応したForm/Entityのクラス単体テスト
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.md
  テストクラスの作成
  テストデータの作成
  文字種と文字列長の単項目精査テストケース
  テストケース表の作成方法
  テストメソッドの作成方法
  その他の単項目精査のテストケース
  項目間精査のテストケース
  setter、getterに対するテストケース
- JUnit 5用拡張機能
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-JUnit5-Extension.md
  Extension クラスと合成アノテーションの一覧