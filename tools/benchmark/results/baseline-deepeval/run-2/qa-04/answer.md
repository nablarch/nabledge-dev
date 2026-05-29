Step 5で回答を生成します。

---

**結論**: Bean Validation対応FormのクラスUnit Testは、`nablarch.test.core.db.EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを記載して`testValidateCharsetAndLength()`や`testSingleValidation()`を呼び出すことで実装する。

---

**根拠**:

## テストクラスの作り方

以下の3条件を満たすテストクラスを作成する：

1. **パッケージ**: テスト対象の Form/Entity と同じパッケージにする
2. **クラス名**: `<Form/Entityクラス名>Test`（例: `UserRegistrationFormTest`）
3. **継承**: `nablarch.test.core.db.EntityTestSupport` を継承する

```java
package com.nablarch.example.app.web.form; // テスト対象Formと同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    /** 文字種・文字列長テスト */
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

    /** setter/getterテスト（Entityの場合に必要） */
    @Test
    public void testSetterAndGetter() {
        String sheetName = "testSetterAndGetter";
        String id = "setterAndGetter";
        testSetterAndGetter(TARGET_CLASS, sheetName, id);
    }
}
```

---

## テストデータの準備方法

### Excelファイルの配置

- **ファイル名**: テストクラスのJavaファイルと同名（拡張子のみ `.xlsx`）
- **配置場所**: テストソースコードと同じディレクトリ
- **セル書式**: 全てのセルを **文字列形式** に設定する（重要）

### シート構成

1テストメソッドにつき1シート。シート名はテストメソッド名と同名を推奨。

---

### ① 文字種・文字列長テスト用シート（`testCharsetAndLength`）

以下のカラムを用意する：

| カラム名 | 内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| allowEmpty | 未入力を許容するか |
| min / max | 最小・最大文字列長（省略可） |
| messageIdWhenEmptyInput | 未入力時の期待メッセージID（省略可） |
| messageIdWhenInvalidLength | 文字列長不適合時の期待メッセージID（省略可） |
| messageIdWhenNotApplicable | 文字種不適合時の期待メッセージ |
| 半角英字 〜 外字 | 各文字種を許容するか（`o` or `x`） |

文字種カラムには `o`（半角小文字のオー）か `x` を設定する。

---

### ② その他の単項目精査テスト用シート（`testSingleValidation`）

| カラム名 | 内容 |
|---|---|
| propertyName | テスト対象のプロパティ名 |
| case | テストケースの説明 |
| input1 | 入力値 |
| messageId | 期待するメッセージID（精査エラーなしの場合は空欄） |

---

### 特殊記法

| 記述 | 意味 |
|---|---|
| `null` | null値 |
| `""` | 空文字列 |
| `${半角英字,5}` | 半角英字5文字 |
| `${全角カタカナ,10}` | 全角カタカナ10文字 |

---

**注意点**:

- **一般的なFormのsetter/getterテスト**: リクエスト単体テストでカバーできるため、クラス単体テストでは通常不要。Entityの場合は自動生成でアプリで使用しないsetter/getterが生成されることがあるため必須。
- **`testSetterAndGetter`でテスト可能な型**: `String`、`BigDecimal`、`java.util.Date`、`valueOf(String)`メソッドを持つクラス（`Integer`、`Long`など）に限定。`List<String>` などはExcelデータから`getParamMap()`で取得して個別にテストを実装する。
- **子Formを持つFormには使用不可**: プロパティとして別のFormを保持する親Formの場合、`testValidateCharsetAndLength`/`testSingleValidation`は使用できないため、独自に精査処理のテストを実装すること。
- **メッセージデータ・コードマスタ**: 静的マスタデータはプロジェクトで管理されたデータがあらかじめ投入されている前提で、個別のテストデータとして作成しない。

参照: `testing-framework-01-entityUnitTestWithBeanValidation.json:s3`, `s2`, `s4`, `s5`, `s6`, `s7`, `s8`, `s9`, `s13`, `s14`, `testing-framework-01-Abstract.json:s9`, `s10`, `s14`, `s16`

---