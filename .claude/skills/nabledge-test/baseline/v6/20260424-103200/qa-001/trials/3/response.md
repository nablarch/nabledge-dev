**結論**: コード値のプルダウン入力は、Nablarchのカスタムタグ `n:codeSelect` タグを使って実装します。`codeId` 属性で使用するコードIDを指定し、必要に応じて `pattern` 属性で表示パターン、`labelPattern` 属性で表示ラベルのフォーマット、`optionColumnName` 属性でオプション名称カラムを指定します。

**根拠**:

コード値専用のカスタムタグとして以下が提供されており、プルダウン表示には `codeSelect` タグを使用します（`libraries-tag.json#s30`）。

- `codeタグ` (コード値)
- `codeSelectタグ` (コード値のプルダウン)
- `codeCheckboxタグ` (コード値のチェックボックス)
- `codeRadioButtonsタグ` (コード値の複数のラジオボタン)
- `codeCheckboxesタグ` (コード値の複数のチェックボックス)

基本的な実装例（JSP）：

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

出力されるHTML：

```html
<!-- 入力画面（"form.gender"が"FEMALE"の場合） -->
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>

<!-- 確認画面 -->
<div>FEMALE-女</div>
```

前提として、コードパターンテーブル（ID, VALUE, PATTERN1, PATTERN2 …）とコード名称テーブル（ID, VALUE, LANG, SORT_ORDER, NAME, SHORT_NAME …）が必要です（`libraries-code.json#s7`）。表示順はコード名称テーブルの `SORT_ORDER` カラムで制御できます（`libraries-code.json#s9`）。

主な属性（`libraries-tag-reference.json#s51`）：

| 属性 | 説明 |
|---|---|
| name (必須) | XHTMLのname属性 |
| codeId (必須) | コードID |
| pattern | 使用するパターンのカラム名（デフォルトは指定なし） |
| optionColumnName | 取得するオプション名称のカラム名 |
| labelPattern | ラベル整形パターン。`$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` のプレースホルダが利用可能。デフォルトは `$NAME$` |
| withNoneOption | リスト先頭に「選択なし」のオプションを追加するか（`true`/`false`） |
| noneOptionLabel | 「選択なし」オプションのラベル |
| multiple, size, disabled, tabindex, onchange, autofocus 等 | 対応するXHTML属性 |

オプション名称（例：`KANA_NAME`）を表示したい場合は、`optionColumnName` と `labelPattern="$OPTIONALNAME$"` を併用します（`libraries-code.json#s10`）：

```jsp
<n:codeSelect name="form.gender" codeId="GENDER"
              optionColumnName="KANA_NAME"
              cssClass="form-control"
              labelPattern="$OPTIONALNAME$"/>
```

プルダウン変更でサブミットしたい場合は、`onchange` 属性でサブミットボタンのクリックイベントを呼び出します（`libraries-tag.json#s16`）：

```jsp
<n:select name="form.plan"
          listName="plans"
          elementLabelProperty="planName"
          elementValueProperty="planId"
          onchange="window.document.getElementById('register').click(); return false;" />
<n:submit id="register" type="submit" uri="register" value="登録" />
```

（コード値ではなく任意のリストをプルダウン表示する場合は、`n:select` タグを使用し、アクション側で選択肢リストをリクエストスコープに設定します。`libraries-tag.json#s9`）

**注意点**:

- カスタムタグでは、言語指定によるコード値の取得はできません。`CodeUtil` がロケール未指定のAPIを呼び出しているためです。言語指定でコード値を取得したい場合は、アクション側で `CodeUtil` を使用して値を取得してください（`libraries-tag.json#s30`）。
- `pattern` 属性で指定する値は、`CodePatternSchema.patternColumnNames` に設定したカラム名と厳密に一致させる必要があります（`libraries-code.json#s7`）。
- `$OPTIONALNAME$` プレースホルダを `labelPattern` で使う場合は、`optionColumnName` 属性の指定が必須です（`libraries-tag-reference.json#s51`）。
- CSP対応時は `onchange` 等の属性にインラインJavaScriptを記載すると `unsafe-inline`/`unsafe-hashes` を許容することになるため、外部スクリプトまたはnonce付きscript要素で動的にバインドすることが推奨されています（`libraries-tag.json#s16`）。

参照:
- `component/libraries/libraries-tag.json#s30`
- `component/libraries/libraries-tag-reference.json#s51`
- `component/libraries/libraries-code.json#s7`
- `component/libraries/libraries-code.json#s9`
- `component/libraries/libraries-code.json#s10`
- `component/libraries/libraries-tag.json#s9`
- `component/libraries/libraries-tag.json#s16`
