**結論**: コードリストのプルダウン入力は、`<n:codeSelect>` タグを使用して実装する。HTMLの `<select>` タグに対応し、`CODE_PATTERN` テーブルと `CODE_NAME` テーブルから選択項目リストを取得する。

**根拠**:

Nablarchでは、コード値を選択/表示するためのカスタムタグとして以下を提供している (web-application-inputAndOutput#s1)。

- codeSelectタグ（`<select>` 出力）
- codeRadioButtonsタグ
- codeCheckboxesタグ
- codeCheckboxタグ
- codeタグ（表示用）

プルダウン（`<select>`）を出力するのは `codeSelect` タグである。

- JSPの実装例 (web-application-inputAndOutput#s2, libraries-07-DisplayTag#s11):

```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

- 主な属性 (libraries-07-DisplayTag#s11, libraries-07-TagReference#s37):
  - `name`（必須・選択項目）: 選択されたコード値をリクエストパラメータ／変数スコープから取得する名前
  - `codeId`（必須）: コードID（CODE_PATTERN/CODE_NAMEテーブルのID）
  - `pattern`: 使用するパターンのカラム名（CODE_PATTERN の PATTERN1〜PATTERN3 等）
  - `optionColumnName`: 取得するオプション名称のカラム名（`$OPTIONALNAME$` 利用時は必須）
  - `labelPattern`: ラベル整形パターン。`$VALUE$`（コード値）/`$NAME$`（コード名称）/`$SHORTNAME$`（略称）/`$OPTIONALNAME$`（オプション名称）のプレースホルダを使う。デフォルトは `$NAME$`
  - `listFormat`: 確認画面用の出力フォーマット（br/div/span/ul/ol/sp）。デフォルト `br`
  - `withNoneOption`: 先頭に「選択なし」オプションを追加するか（true/false、デフォルト false）
  - `noneOptionLabel`: `withNoneOption="true"` 時の先頭オプションのラベル

- HTML出力例（入力画面／確認画面）(libraries-07-DisplayTag#s11):

```html
<!-- 入力画面 -->
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>

<!-- 確認画面（listFormat="div"） -->
<div>03:処理実行中-実行-0002-03-ja</div>
```

- 初期値の設定 (web-application-inputAndOutput#s11): Actionクラスでリクエストスコープに値を設定する（例: `form.setStatus("03")` → `ctx.setRequestScopedVar("batch", batch)`）。JSP側に追加処理は不要で、`name` 属性と値の対応によって選択状態が反映される。

なお、任意のリスト（DBから取得した独自のラベル／値など、コード管理機能に依存しない選択肢）でプルダウンを作る場合は、汎用の `<n:select>` タグを使う（例: `<n:select name="W11AC02.groupIds" listName="allGroups" elementLabelProperty="name" elementValueProperty="id" ... />`）(web-application-inputAndOutput#s11)。

**注意点**:
- `codeSelect` タグは CODE_PATTERN / CODE_NAME テーブルに依存するため、コード管理機能のテーブル定義・データ投入が前提。
- `$OPTIONALNAME$` を `labelPattern` で使用する場合、`optionColumnName` の指定が必須。
- `listFormat` は codeSelect では **確認画面用の出力にのみ** 適用される（入力画面の `<select>` 出力には影響しない）。
- 入力／選択項目の初期値設定は Action 側でリクエストスコープに値を格納する。`name` 属性の値と Action 側のキーを一致させる必要がある。

参照:
- guide/web-application/web-application-inputAndOutput.json#s1
- guide/web-application/web-application-inputAndOutput.json#s2
- guide/web-application/web-application-inputAndOutput.json#s11
- component/libraries/libraries-07-DisplayTag.json#s9
- component/libraries/libraries-07-DisplayTag.json#s11
- component/libraries/libraries-07-TagReference.json#s37
