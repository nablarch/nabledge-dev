**結論**: Nablarch 6 でコード値のプルダウン入力を実装するには、Jakarta Server Pages カスタムタグの **`<n:codeSelect>` タグ** を使用します。コード管理機能（`libraries-code`）に登録されたコード値を、プルダウン（HTMLの`<select>`要素）として画面に出力できます。

**根拠**:

1. コード値専用の選択項目タグとして `codeSelect` タグが提供されています（`libraries-tag.json#s30`）。

    > - `codeタグ` (コード値)
    > - `codeSelectタグ` (コード値のプルダウン)
    > - `codeCheckboxタグ` (コード値のチェックボックス)
    > - `codeRadioButtonsタグ` (コード値の複数のラジオボタン)
    > - `codeCheckboxesタグ` (コード値の複数のラジオチェックボックス)

2. **実装例（JSP）**（`libraries-tag.json#s30`）:

    ```jsp
    <n:codeSelect name="form.gender"
                  codeId="GENDER" pattern="PATTERN2"
                  labelPattern="$VALUE$-$SHORTNAME$"
                  listFormat="div" />
    ```

    出力されるHTML（`form.gender` が `"FEMALE"` の場合）:
    ```html
    <!-- 入力画面 -->
    <select name="form.gender">
      <option value="MALE">MALE-男</option>
      <option value="FEMALE" selected="selected">FEMALE-女</option>
    </select>

    <!-- 確認画面 -->
    <div>FEMALE-女</div>
    ```

3. **主な属性**（`libraries-tag-reference.json#s51` codeSelectタグ）:
    - `name` (必須): XHTMLのname属性
    - `codeId` (必須): コードID
    - `pattern`: 使用するパターンのカラム名
    - `optionColumnName`: 取得するオプション名称のカラム名
    - `labelPattern`: ラベル整形パターン。プレースホルダ `$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` を使用可（デフォルトは `$NAME$`）
    - `listFormat`: リスト表示フォーマット（br/div/span/ul/ol/sp）
    - `withNoneOption` / `noneOptionLabel`: 先頭に「選択なし」オプションを追加
    - `multiple`, `size`, `disabled`, `tabindex`, `onfocus`, `onblur`, `onchange`, `autofocus`, `errorCss`, `nameAlias` など

4. 汎用の選択肢を使うプルダウン（コード管理を使わない場合）は `<n:select>` タグを使用し、アクション側で `List<Plan>` のような選択肢リストをリクエストスコープに設定したうえで、`listName` / `elementLabelProperty` / `elementValueProperty` を指定します（`libraries-tag.json#s9`）。

**注意点**:

- カスタムタグでは **言語指定によるコード値取得はできません**（`CodeUtil` のロケールを指定しないAPIを内部で使用しているため）。言語を切り替えたい場合は、アクション側で `CodeUtil` を使ってコード値を取得する必要があります（`libraries-tag.json#s30`）。
- コード値を使うには、事前に **コード管理機能のテーブル（コードパターンテーブル／コード名称テーブル）への登録と初期設定** が必要です。
- `labelPattern` で `$OPTIONALNAME$` を使う場合は、`optionColumnName` 属性の指定が必須です。
- 確認画面時は `<select>` ではなく `<div>` 形式で選択値のラベルのみが出力される点に注意。

参照:
- `component/libraries/libraries-tag.json#s30`
- `component/libraries/libraries-tag.json#s9`
- `component/libraries/libraries-tag-reference.json#s51`
- `component/libraries/libraries-tag-reference.json#s30`
