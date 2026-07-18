### Answer

Bean ValidationのFormクラス単体テストは、以下の手順で作成します。

---

## 1. テストクラスの作成

以下の条件を満たすテストクラスを作成します。

- **パッケージ**: テスト対象のForm/Entityと同じパッケージ
- **クラス名**: `<Form/Entityクラス名>Test`
- **継承**: `nablarch.test.core.db.EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    // テストメソッドはここに記述
}
```

---

## 2. テストデータ（Excel）の準備

テストデータはExcelファイルで管理します。

- **配置場所**: テストソースコードと同じディレクトリ
- **ファイル名**: テストクラスと同じ名前（拡張子のみ `.xlsx`）
  - 例: `UserRegistrationFormTest.java` → `UserRegistrationFormTest.xlsx`
- 各テスト種別が1シートずつ使用します

---

## 3. テストメソッドの種類と書き方

### (1) 文字種・文字列長の単項目精査

`testValidateCharsetAndLength()` を使用します。

```java
@Test
public void testCharsetAndLength() {
    String sheetName = "testCharsetAndLength";
    String id = "charsetAndLength";
    testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
}
```

**Excelシートのカラム構成:**

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `allowEmpty` | 未入力を許容するか |
| `group` | Bean Validationのグループ（省略可） |
| `min` / `max` | 最小・最大文字列長（省略可） |
| `messageIdWhenEmptyInput` | 未入力時の期待メッセージ（省略可） |
| `messageIdWhenInvalidLength` | 文字列長不適合時の期待メッセージ（省略可） |
| `messageIdWhenNotApplicable` | 文字種不適合時の期待メッセージ |
| `半角英字`, `半角数字`, ... | 各文字種を許容するか（`o` or `x`） |

### (2) その他の単項目精査（日付フォーマット等）

`testSingleValidation()` を使用します。

```java
@Test
public void testSingleValidation() {
    String sheetName = "testSingleValidation";
    String id = "singleValidation";
    testSingleValidation(TARGET_CLASS, sheetName, id);
}
```

**Excelシートのカラム構成:**

| カラム名 | 内容 |
|---|---|
| `propertyName` | テスト対象のプロパティ名 |
| `case` | テストケースの説明 |
| `group` | Bean Validationのグループ（省略可） |
| `input1` | 入力値 |
| `messageId` | 期待するメッセージID（エラーなしの場合は空欄） |
| `interpolateKey_n` / `interpolateValue_n` | 埋め込み文字（省略可） |

> **注意**: プロパティとして別のFormを保持するFormには使用できません。その場合は独自実装が必要です。

### (3) 項目間精査（Bean Validationのクラスレベル制約）

`testBeanValidation()` を使用します。

```java
@Test
public void testWholeFormValidation() {
    String sheetName = "testWholeFormValidation";
    testBeanValidation(TARGET_CLASS, sheetName);
}
```

---

## まとめ

| テスト種別 | スーパークラスのメソッド | 主な用途 |
|---|---|---|
| 文字種・文字列長 | `testValidateCharsetAndLength` | 入力許容文字種と長さの検証 |
| その他の単項目精査 | `testSingleValidation` | 日付フォーマット等の個別精査 |
| 項目間精査 | `testBeanValidation` | クラスレベルの相関チェック |

サンプルファイルは `UserRegistrationFormTest.java` / `UserRegistrationFormTest.xlsx` / `UserRegistrationForm.java` が参照例として提供されています。