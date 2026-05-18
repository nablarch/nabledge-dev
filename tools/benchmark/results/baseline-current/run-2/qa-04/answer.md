**結論**: Bean ValidationのFormクラス単体テストは、`EntityTestSupport`を継承したテストクラスを作成し、Excelファイルにテストデータを記載して実行します。

### テストクラスの作り方

以下の条件を満たすテストクラスを作成します。

- **パッケージ**: テスト対象のForm/Entityと同じパッケージ
- **クラス名**: `<Form名>Test`（例: `UserRegistrationFormTest`）
- **継承**: `nablarch.test.core.db.EntityTestSupport` を継承

```java
package com.nablarch.example.app.web.form; // テスト対象と同じパッケージ

import nablarch.test.core.db.EntityTestSupport;
import org.junit.Test;

public class UserRegistrationFormTest extends EntityTestSupport {

    private static final Class<?> TARGET_CLASS = UserRegistrationForm.class;

    @Test
    public void testCharsetAndLength() {
        String sheetName = "testCharsetAndLength";
        String id = "charsetAndLength";

        // スーパクラスのメソッドを呼び出してテスト実行
        testValidateCharsetAndLength(TARGET_CLASS, sheetName, id);
    }
}
```

`testValidateCharsetAndLength(Class, String, String)` を呼び出すと、テストデータの各行に対して文字種・文字列長・未入力などの観点が自動的にテストされます。

### テストデータ（Excelファイル）の準備方法

テストデータは **テストクラスと同じディレクトリ** に、**同じ名前・拡張子のみ`.xlsx`** で配置します。

Excelシートに用意するカラム:
- `propertyName`: テスト対象のプロパティ名
- `allowEmpty`: 未入力を許容するか
- `group`: Bean Validationのグループ（省略可）
- `min`: 許容する最小文字列長（省略可）
- `max`: 許容する最大文字列長（省略可）
- `messageIdWhenEmptyInput`: 未入力時の期待メッセージ（省略可）
- `messageIdWhenInvalidLength`: 文字列長不適合時の期待メッセージ（省略可）
- `messageIdWhenNotApplicable`: 文字種不適合時の期待メッセージ
- `半角英字`〜`外字`: 各文字種を許容するか（`o`=許容、`x`=不許容）

**注意点**:
- メッセージデータやコードマスタなどの静的マスタデータは、プロジェクト管理データがあらかじめ投入されている前提です。個別のテストデータとして作成する必要はありません。
- Bean Validationのグループを指定する場合、内部クラスは `$` で区切ってFQCNで指定します（例: `com.example.Form$GroupA`）。
- テストデータは精査テスト用シートとsetter/getter用シートで1シートずつ使用する前提です。

参照: `development-tools/testing-framework/testing-framework-01-entityUnitTestWithBeanValidation.json#s1`, `#s2`, `#s3`, `#s5`, `#s6`