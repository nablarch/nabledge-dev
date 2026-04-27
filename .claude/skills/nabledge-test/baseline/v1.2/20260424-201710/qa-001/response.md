**結論**: コードリスト（コード管理機能のコード値）からプルダウン（HTMLのselectタグ）を生成するには、`<n:codeSelect>` タグを使用します。`codeId` 属性（必須）でコードIDを指定し、`pattern` 属性で使用するCODE_PATTERNテーブルのカラム名を指定します。コード管理機能を使わずに任意のリストからプルダウンを作る場合は、`<n:select>` タグを使用します。

**根拠**:

1. コード値の選択／表示用カスタムタグとして、フレームワークは次を提供しています。`codeSelect` / `codeRadioButtons` / `codeCheckboxes` / `codeCheckbox` / `code` のうち、selectタグ（プルダウン）を出力するのは `codeSelect` タグです。これらは `CODE_PATTERN` テーブルと `CODE_NAME` テーブルを使用します。（参照: web-application-inputAndOutput.json#s1、libraries-07-DisplayTag.json#s9）

2. `codeSelect` タグの実装例（JSP）:
   ```jsp
   <n:codeSelect name="W11AF01.status"
                 codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
                 labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
                 listFormat="div" />
   ```
   出力されるHTML:
   ```html
   <select name="W11AF01.status">
       <option value="01">01:初期状態-初期-0002-01-ja</option>
       <option value="02">02:処理開始待ち-待ち-0002-02-ja</option>
   </select>
   ```
   （参照: web-application-inputAndOutput.json#s2）

3. 共通属性（codeSelect／codeRadioButtons／codeCheckboxes／codeタグで共通）:
   - `name`（選択項目では必須）: 選択されたコード値をリクエストパラメータから取得する際のname属性。
   - `codeId`（必須）: コードID。
   - `pattern`: 使用するパターンのカラム名。
   - `optionColumnName`: 取得するオプション名称のカラム名。
   - `labelPattern`: ラベル整形パターン。プレースホルダは `$VALUE$`（コード値）、`$NAME$`（コード名称）、`$SHORTNAME$`（コード略称）、`$OPTIONALNAME$`（オプション名称）。デフォルトは `"$NAME$"`。`$OPTIONALNAME$` を使う場合は `optionColumnName` 必須。
   - `listFormat`: リスト表示フォーマット（br／div／span／ul／ol／sp）。codeSelect では確認画面用の出力にのみ使用される。
   - `withNoneOption`: リスト先頭に「選択なし」オプションを追加するか（デフォルトfalse）。
   - `noneOptionLabel`: 「選択なし」のラベル（withNoneOption=true のときのみ有効）。
   （参照: libraries-07-DisplayTag.json#s11、libraries-07-TagReference.json#s37）

4. コード管理機能を使わず、任意のリスト（例: DBから取得したグループ一覧）からプルダウンを作る場合は `<n:select>` タグを使用します。
   ```jsp
   <n:select name="W11AC02.groupIds" multiple="true"
             listName="allGroups" elementLabelProperty="name" elementValueProperty="id"
             elementLabelPattern="$VALUE$ - $LABEL$" listFormat="ul" />
   ```
   `listName`（選択項目リストの属性名）、`elementLabelProperty`／`elementValueProperty`（リスト要素からラベル・値を取得するプロパティ名）がいずれも必須。初期値を設定する場合は、Action クラスでリクエストスコープにリストと選択値を登録します。（参照: web-application-inputAndOutput.json#s11、libraries-07-FormTagList.json#s7、libraries-07-TagReference.json#s16）

**注意点**:
- `codeSelect` は選択されたコード値に対応するラベルを CODE_NAME テーブルから自動取得します。事前に CODE_PATTERN／CODE_NAME テーブルへ該当コードを登録しておく必要があります。
- 初期値（selected）を設定する場合は、Action クラスでリクエストスコープに `name` 属性の値に対応するコード値を設定します（例: `batch.setStatus("03")` → `ctx.setRequestScopedVar("batch", batch)`）。
- `listFormat` は codeSelect では確認画面の出力時のみ使用されます（入力画面は常にselect形式で出力）。
- 「選択なし」を先頭に追加したい場合は `withNoneOption="true"` と `noneOptionLabel` を指定します。`<n:select>` 側でも同じ属性が使えます（選択なしオプションのvalue属性は常に空文字）。
- コード管理機能を使うかどうかで `n:codeSelect` と `n:select` を使い分けてください。表示専用（一覧画面等）なら `n:code` タグを使用します。

参照:
- guide/web-application/web-application-inputAndOutput.json#s1, s2, s8, s9, s11
- component/libraries/libraries-07-DisplayTag.json#s9, s11, s12, s14
- component/libraries/libraries-07-TagReference.json#s16, s37
- component/libraries/libraries-07-FormTagList.json#s7
- component/libraries/libraries-07-FormTag.json#s17
