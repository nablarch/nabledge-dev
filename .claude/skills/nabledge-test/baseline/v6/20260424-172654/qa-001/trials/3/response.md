**結論**: コード値のプルダウン入力を実装するには、カスタムタグの `<n:codeSelect>` タグを使用します。`name` 属性に画面項目名、`codeId` 属性に表示対象のコードIDを指定することで、コード管理機能から取得したコード値を select(プルダウン) として出力できます。

**根拠**:

基本的な使用方法 (libraries-tag.json#s30):

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

出力されるHTML:
```html
<!-- 入力画面 -->
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>

<!-- 確認画面 -->
<div>FEMALE-女</div>
```

主な属性 (libraries-tag-reference.json#s51):

| 属性 | 説明 |
|---|---|
| name (必須) | XHTMLのname属性 |
| codeId (必須) | コードID |
| pattern | 使用するパターンのカラム名。機能ごとに表示/非表示を切り替える場合に指定 |
| optionColumnName | 取得するオプション名称のカラム名 |
| labelPattern | ラベル整形用パターン。プレースホルダは `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値） |
| listFormat | 確認画面でのリスト表示形式 (br/div/span/ul/ol/sp)。デフォルトは br |
| withNoneOption | リスト先頭に「選択なし」オプションを追加する場合は `true`。デフォルト `false` |
| noneOptionLabel | withNoneOption=true の場合のラベル |
| size / multiple / disabled / tabindex / onfocus / onblur / onchange / autofocus | XHTML/HTML5の対応属性 |

パターンによる表示切替 (libraries-code.json#s7): コードパターンテーブルに `PATTERN1`/`PATTERN2` のようなパターン列を定義し、pattern 属性で指定することで機能ごとの表示項目を切り替えられます。

オプション名称の利用 (libraries-code.json#s10): 名称・略称以外の表示名称を使用する場合は、コード名称テーブルにオプション名称カラム（例: `KANA_NAME`）を定義し、`optionColumnName="KANA_NAME"` と `labelPattern="$OPTIONALNAME$"` を指定します。

ソート順 (libraries-code.json#s9): 表示順序はコード名称テーブルの `SORT_ORDER` カラムで制御します（言語ごとに定義可能）。

**注意点**:
- カスタムタグでは言語指定によるコード値取得はできません（`CodeUtil` のロケール非指定APIを使用しているため）。言語指定が必要な場合は、アクション側で `CodeUtil` を使って値を取得してください (libraries-tag.json#s30)。
- `$OPTIONALNAME$` を labelPattern で使用する場合、`optionColumnName` 属性の指定が必須です。
- pattern 属性で指定する値は、`CodePatternSchema.patternColumnNames` に設定したカラム名と厳密に一致させる必要があります。

参照:
- component/libraries/libraries-tag.json#s30 (codeSelectタグ 実装例)
- component/libraries/libraries-tag-reference.json#s51 (codeSelectタグ 属性仕様)
- component/libraries/libraries-code.json#s7 (パターンによる表示切替)
- component/libraries/libraries-code.json#s9 (ソート順)
- component/libraries/libraries-code.json#s10 (オプション名称)
