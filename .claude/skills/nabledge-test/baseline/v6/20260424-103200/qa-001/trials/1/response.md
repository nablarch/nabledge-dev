**結論**: コード値のプルダウン入力を実装するには、カスタムタグの `n:codeSelect` タグを使用します。必須属性は `name`（フォームプロパティ名）と `codeId`（コードID）で、必要に応じて `pattern`、`optionColumnName`、`labelPattern`、`withNoneOption`、`noneOptionLabel` などの属性で表示を制御します。コード値のマスタは、コードパターンテーブルとコード名称テーブルで管理します。

**根拠**:

JSPでの実装例（GENDERコードのプルダウン）:

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

コードマスタのテーブル構成:

- コードパターンテーブル: `ID`, `VALUE`, `PATTERN1`, `PATTERN2` … の列を持ち、機能毎に表示するコードの組合せ（パターン）を制御。
- コード名称テーブル: `ID`, `VALUE`, `LANG`, `SORT_ORDER`, `NAME`, `SHORT_NAME`（およびオプション名称カラム）を保持し、表示名称・略称・ソート順・多言語名称を定義。

主な属性（codeSelectタグ）:

| 属性 | 説明 |
|---|---|
| name（必須） | XHTMLのname属性（バインドするフォームプロパティ）|
| codeId（必須） | コードID |
| pattern | 使用するパターンのカラム名。機能毎に表示対象を切り替える |
| optionColumnName | 取得するオプション名称のカラム名（`$OPTIONALNAME$` 使用時は必須）|
| labelPattern | ラベル整形パターン。プレースホルダ `$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$`。デフォルトは `$NAME$` |
| listFormat | 確認画面等でリスト表示する際のフォーマット（br/div/span/ul/ol/sp）|
| withNoneOption | 先頭に「選択なし」オプションを追加するか（`true`/`false`、デフォルト `false`）|
| noneOptionLabel | `withNoneOption="true"` 時に使う先頭オプションのラベル |

パターン例 / オプション名称表示例も含まれる。ソート順はコード名称テーブルの `SORT_ORDER` カラムで制御。

**注意点**:

- カスタムタグでは **言語指定によるコード値の取得はできません**。アクション側で `CodeUtil` を使用してください。
- `pattern` に指定する値は、`CodePatternSchema.patternColumnNames` で設定したカラム名と厳密に一致させる必要があります。
- `labelPattern` で `$OPTIONALNAME$` を使う場合は、`optionColumnName` 属性の指定が必須です。
- 確認画面では `<select>` ではなく `listFormat` で指定した要素（例: `div`）で出力されます。

参照:
- `component/libraries/libraries-tag.json#s30`
- `component/libraries/libraries-tag-reference.json#s51`
- `component/libraries/libraries-code.json#s7`
- `component/libraries/libraries-code.json#s9`
- `component/libraries/libraries-code.json#s10`
