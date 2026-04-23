**結論**: コード値のプルダウン入力は、Nablarchカスタムタグの `<n:codeSelect>` タグを使って実装する。`codeId` 属性でコードIDを指定すれば、 [コード管理](../../component/libraries/libraries-code.md) に登録されたコード値を選択肢としたプルダウンが自動生成される。

**根拠**:

1. コード値専用のカスタムタグとして以下が提供されている（`libraries-tag.json#s30`）：
   - `codeタグ` (コード値)
   - `codeSelectタグ` (コード値のプルダウン)
   - `codeCheckboxタグ` / `codeCheckboxesタグ` / `codeRadioButtonsタグ`

2. JSP実装例（`libraries-tag.json#s30`）：
   ```jsp
   <n:codeSelect name="form.gender"
                 codeId="GENDER" pattern="PATTERN2"
                 labelPattern="$VALUE$-$SHORTNAME$"
                 listFormat="div" />
   ```
   出力HTML（入力画面）:
   ```html
   <select name="form.gender">
     <option value="MALE">MALE-男</option>
     <option value="FEMALE" selected="selected">FEMALE-女</option>
   </select>
   ```

3. `codeSelect` タグの主な属性（`libraries-tag-reference.json#s51`）：
   - `name` `必須`: XHTMLのname属性
   - `codeId` `必須`: コードID
   - `pattern`: 使用するパターンのカラム名（選択肢の絞り込み）
   - `labelPattern`: ラベルフォーマット。`$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` のプレースホルダが使用可能。デフォルトは `$NAME$`
   - `withNoneOption`: 先頭に「選択なし」を追加するか（true/false、デフォルト false）
   - `noneOptionLabel`: 選択なしのラベル
   - `optionColumnName`: `$OPTIONALNAME$` 使用時に必須
   - `multiple` / `size` / `disabled` / `onchange` 等のXHTML属性も指定可

4. 入力値チェックは `@CodeValue` アノテーションで実装可能（`libraries-code.json#s11`）：
   ```java
   @CodeValue(codeId = "GENDER", pattern = "PATTERN2")
   private String gender;
   ```

**注意点**:
- カスタムタグは `CodeUtil` のロケールを指定しないAPIを使うため、**言語指定によるコード値取得はできない**。多言語対応で言語指定が必要な場合は、アクション側で `CodeUtil` を使って値を取得する（`libraries-tag.json#s30`）。
- 選択できる値を `pattern` で制限した場合は、バリデーション側でも同じ `pattern` を指定して整合性を取る必要がある（`libraries-code.json#s11`）。
- コード管理テーブル（コードパターンテーブル・コード名称テーブル）へのコード値登録が前提（`libraries-tag.json#s30`）。

参照:
- component/libraries/libraries-tag.json#s30
- component/libraries/libraries-tag.json#s9
- component/libraries/libraries-tag-reference.json#s51
- component/libraries/libraries-tag-reference.json#s55
- component/libraries/libraries-code.json#s11
