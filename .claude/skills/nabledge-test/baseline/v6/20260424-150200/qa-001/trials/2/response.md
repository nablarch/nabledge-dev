**結論**: コード値のプルダウン入力は、Nablarch が提供するカスタムタグ `<n:codeSelect>` を使用して実装します。`codeId` 属性で表示対象のコードIDを指定することで、コード管理機能に登録されたコード名称テーブルの値をプルダウン（HTMLの `<select>`）として自動的に出力できます。必要に応じて `pattern`（表示パターンの絞り込み）、`labelPattern`（ラベル整形）、`optionColumnName`（オプション名称）、`withNoneOption`（先頭に「選択なし」オプション追加）などの属性で挙動を制御します。入力値の妥当性チェックには `@CodeValue` アノテーションを使用します。

**根拠**:

1. コード値専用カスタムタグの一覧（`libraries-tag.json#s30`）
   - `codeタグ`（コード値表示）
   - `codeSelectタグ`（**コード値のプルダウン**）
   - `codeCheckboxタグ`／`codeRadioButtonsタグ`／`codeCheckboxesタグ`

2. `n:codeSelect` の基本実装例（`libraries-tag.json#s30`）

   ```jsp
   <n:codeSelect name="form.gender"
                 codeId="GENDER" pattern="PATTERN2"
                 labelPattern="$VALUE$-$SHORTNAME$"
                 listFormat="div" />
   ```

   出力されるHTML（入力画面）:
   ```html
   <select name="form.gender">
     <option value="MALE">MALE-男</option>
     <option value="FEMALE" selected="selected">FEMALE-女</option>
   </select>
   ```

3. 表示パターンによる絞り込み（`libraries-code.json#s7`）

   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
   ```

4. オプション名称の利用（`libraries-code.json#s10`）

   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER"
                 optionColumnName="KANA_NAME" labelPattern="$OPTIONALNAME$"/>
   ```

5. `codeSelectタグ` の主要属性（`libraries-tag-reference.json#s51`）
   - `name`（必須）、`codeId`（必須）、`pattern`、`optionColumnName`、`labelPattern`
   - `size` / `multiple` / `disabled` / `onchange` 等のHTML属性
   - `listFormat`、`withNoneOption`、`noneOptionLabel`

6. 入力値のバリデーション（`libraries-code.json#s11`）

   ```java
   @CodeValue(codeId = "GENDER")
   private String gender;
   ```
   パターン絞り込み:
   ```java
   @CodeValue(codeId = "GENDER", pattern = "PATTERN2")
   private String gender;
   ```

**注意点**:
- `n:codeSelect` などコード値系カスタムタグは **言語指定によるコード値取得ができません**（`libraries-tag.json#s30`, `libraries-code.json#s8`）。
- パターンで選択肢を絞り込んだ場合は、サーバー側バリデーションにも同じ `pattern` を指定（`libraries-code.json#s11`）。
- 一般的な（コード値でない）選択肢のプルダウンには `<n:select>` タグを使用（`libraries-tag.json#s9`）。
- プルダウン変更時にサブミットさせたい場合は、`onchange` 属性でサブミットボタンの `click()` を呼ぶ（`libraries-tag.json#s16`）。

参照:
- `component/libraries/libraries-tag.json#s30`
- `component/libraries/libraries-tag-reference.json#s51`
- `component/libraries/libraries-code.json#s7, s10, s11, s8`
- `component/libraries/libraries-tag.json#s9, s16`
