**結論**: コード値のプルダウン入力は、Nablarchが提供するカスタムタグ `<n:codeSelect>` を使用して実装します。`codeId` 属性で対象のコードIDを指定し、必要に応じて `pattern` 属性や `labelPattern` 属性で表示を制御します。

**根拠**:

基本的な実装例（JSP）:
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

主な属性（`codeSelect`タグ）:
- `name` (必須): XHTMLのname属性
- `codeId` (必須): コードID
- `pattern`: 使用するパターンのカラム名（表示するコード値の絞り込み）
- `optionColumnName`: 取得するオプション名称のカラム名
- `labelPattern`: ラベルを整形するパターン。プレースホルダとして `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）が使える。デフォルトは `$NAME$`
- `size`, `multiple`, `disabled`, `tabindex`, `onchange` などのHTML標準属性
- `withNoneOption`: リスト先頭に選択なしのオプションを追加するか否か（デフォルト `false`）
- `noneOptionLabel`: 選択なしオプションのラベル（デフォルト `""`）
- `errorCss`: エラー時のCSSクラス名（デフォルト `nablarch_error`）
- `nameAlias`: name属性のエイリアス（カンマ区切りで複数指定可）

オプション名称を表示する例:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" optionColumnName="KANA_NAME"
              cssClass="form-control" labelPattern="$OPTIONALNAME$"/>
```

入力値の妥当性チェック（Bean Validation）:
```java
@CodeValue(codeId = "GENDER")
private String gender;

// パターンを絞り込む場合
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

**注意点**:
- カスタムタグでは、**言語指定によるコード値の取得はできない**。`CodeUtil` のロケールを指定しないAPIを内部で使用しているため。言語指定が必要な場合は、アクション側で `CodeUtil` を使用して値を取得する。
- 表示順は、コード名称テーブルの `SORT_ORDER` カラムで制御する（言語ごとに設定可能）。
- 表示対象を絞り込みたい場合は、コードパターンテーブルにパターン列（例: `PATTERN1`, `PATTERN2`）を定義し、`pattern` 属性で指定する。パターン列は `CodePatternSchema.patternColumnNames` に設定する必要がある。
- `$OPTIONALNAME$` を `labelPattern` に指定する場合は、`optionColumnName` 属性の指定が必須。
- 入力画面でパターン絞り込みを使っている場合、バリデーション側でも同じパターンを指定しないと整合が取れない（`@CodeValue(codeId = "...", pattern = "...")`）。
- ドメインバリデーションでは1つのドメインに対して1つのパターンしか指定できないため、複数パターンを扱うにはパターン別のドメインを定義する。

参照:
- `component/libraries/libraries-tag.json#s30`
- `component/libraries/libraries-tag-reference.json#s51`
- `component/libraries/libraries-code.json#s7`
- `component/libraries/libraries-code.json#s9`
- `component/libraries/libraries-code.json#s10`
- `component/libraries/libraries-code.json#s11`
