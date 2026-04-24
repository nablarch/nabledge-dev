**結論**: コード値のプルダウン入力は、Nablarch が提供するカスタムタグ `<n:codeSelect>` を使用して実装します。`name` 属性と `codeId` 属性が必須で、コード管理機能に登録されたコード情報を元に `<select>` 要素を自動生成します。

**根拠**:

JSP での基本実装例 (`libraries-tag.json#s30`):

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

主な属性 (`libraries-tag-reference.json#s51`):

| 属性 | 説明 |
|---|---|
| `name` (必須) | XHTMLのname属性 |
| `codeId` (必須) | コードID |
| `pattern` | 使用するパターンのカラム名 |
| `optionColumnName` | 取得するオプション名称のカラム名 |
| `labelPattern` | ラベル整形パターン。`$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` のプレースホルダが使用可能 |
| `withNoneOption` | リスト先頭に「選択なし」のオプションを追加するか |
| `noneOptionLabel` | 「選択なし」オプションのラベル |
| `size`, `multiple`, `disabled`, `onchange`, `autofocus` 等 | 標準のXHTML/HTML5属性 |

パターン指定で表示項目を切り替える例 (`libraries-code.json#s7`):

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

オプション名称を表示する例 (`libraries-code.json#s10`):

```jsp
<n:codeSelect name="form.gender" codeId="GENDER"
              optionColumnName="KANA_NAME"
              cssClass="form-control"
              labelPattern="$OPTIONALNAME$"/>
```

前提として、コード管理機能（CodeUtil／コードパターンテーブル／コード名称テーブル）の初期設定が必要です。

**注意点**:
- `codeSelect` などのカスタムタグでは**言語指定によるコード値の取得はできません** (`libraries-code.json#s8`, `libraries-tag.json#s30`)。
- 表示順は **コード名称テーブルの `SORT_ORDER` カラム** で制御します (`libraries-code.json#s9`)。
- `labelPattern` で `$OPTIONALNAME$` を使用する場合は `optionColumnName` 属性の指定が必須です。
- プルダウン変更を契機にサブミットしたい場合は、`onchange` 属性でサブミットボタンの click イベントを呼び出します (`libraries-tag.json#s16`)。
- コード値以外の任意の選択肢をプルダウン表示する場合は、`<n:codeSelect>` ではなく `<n:select>` タグを使用します (`libraries-tag.json#s9`)。

参照:
- `component/libraries/libraries-tag.json#s30` (codeSelectタグ実装例)
- `component/libraries/libraries-tag-reference.json#s51` (codeSelectタグ属性リファレンス)
- `component/libraries/libraries-code.json#s7` (パターン指定)
- `component/libraries/libraries-code.json#s10` (オプション名称)
- `component/libraries/libraries-code.json#s9` (ソート順)
- `component/libraries/libraries-code.json#s8` (多言語化)
- `component/libraries/libraries-tag.json#s9` (汎用プルダウン `n:select`)
- `component/libraries/libraries-tag.json#s16` (プルダウン変更でサブミット)
