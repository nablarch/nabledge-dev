**結論**: コードリスト（コード管理機能で管理するコード値）をプルダウン入力で実装するには、`<n:codeSelect>` カスタムタグを使用します。コード管理機能を使わず、任意の値リストを表示するだけであれば `<n:select>` タグを使用します。UIフレームワーク（ウィジェット）を用いる場合は「コード値プルダウン入力項目ウィジェット」を利用し、`codeId` 属性でコードIDを指定します。

**根拠**:

1. **codeSelectタグによるプルダウン実装（コード管理機能連携）**

   `<n:codeSelect>` は HTML の `<select>` タグを出力するカスタムタグで、CODE_PATTERN / CODE_NAME テーブルから取得したコード値を選択項目リストとして表示します。

   JSP 実装例：
   ```jsp
   <n:codeSelect name="W11AF01.status"
                 codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
                 labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
                 listFormat="div" />
   ```

   出力 HTML 例：
   ```html
   <select name="W11AF01.status">
       <option value="01">01:初期状態-初期-0002-01-ja</option>
       <option value="02">02:処理開始待ち-待ち-0002-02-ja</option>
   </select>
   ```

2. **codeSelectタグの主な属性**

   | 属性 | 説明 |
   |---|---|
   | `name`（必須） | 選択されたコード値を取得するためのリクエストパラメータ名 |
   | `codeId`（必須） | コードID |
   | `pattern` | 使用するパターンのカラム名（例：PATTERN1） |
   | `optionColumnName` | 取得するオプション名称のカラム名 |
   | `labelPattern` | ラベル整形パターン。プレースホルダ `$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` が使用可能（デフォルト `$NAME$`） |
   | `withNoneOption` | リスト先頭に「選択なし」オプションを追加するか（デフォルト false） |
   | `noneOptionLabel` | 選択なしオプションのラベル（`withNoneOption="true"` のとき有効） |
   | `multiple` | XHTML の multiple 属性 |
   | `size` | XHTML の size 属性 |

3. **初期値設定**

   Action クラスで JSP 遷移前にリクエストスコープに初期値を設定します。複数選択の場合は、初期値と選択候補リストの両方を設定します。

   ```java
   String[] defaultGroups = {"group2", "group3"};
   Map<String, String> form = new HashMap<String, String>();
   form.put("groupIds", defaultGroups);
   ctx.setRequestScopedVar("W11AC02", form);
   ```

4. **UIフレームワークのコード値プルダウン入力項目ウィジェット**

   ウィジェットを使う場合、`/WEB-INF/tags/widget/field/code_pulldown.tag` を利用し、`codeId` 属性（必須）でコードIDを指定します。`pattern` / `optionColumnName` / `labelPattern` / `withNoneOption` 属性を `<n:codeSelect>` と同様に扱えます。`sample` 属性を指定するとローカル動作時にダミー値を表示できます（サーバ動作時は `codeId` から取得）。

5. **コード管理機能を使わない場合**

   任意のリストを元にプルダウンを出す場合は `<n:select>` タグを利用し、`listName` / `elementLabelProperty` / `elementValueProperty` / `elementLabelPattern` 属性でリスト要素との対応を指定します。

**注意点**:
- `codeSelect` / `codeRadioButtons` / `codeCheckboxes` / `codeCheckbox` の 4 タグはコード管理機能と連携するタグです。選択肢の表示にはコード管理テーブル（CODE_PATTERN / CODE_NAME）が必要です。
- `listFormat` 属性は `codeSelect` タグでは確認画面用出力時のみ使用されます（入力画面の `<select>` には適用されません）。
- ウィジェットの `codeId` と `sample` を両方指定するとローカル動作時は `sample` の値が優先されます。
- `$OPTIONALNAME$` をラベルパターンで使う場合は `optionColumnName` 属性の指定が必須です。

参照: `component/libraries/libraries-07-DisplayTag.json#s9`, `component/libraries/libraries-07-DisplayTag.json#s11`, `component/libraries/libraries-07-TagReference.json#s37`, `component/ui-framework/ui-framework-field-code-pulldown.json#s2`, `component/ui-framework/ui-framework-field-code-pulldown.json#s3`, `guide/web-application/web-application-inputAndOutput.json#s2`, `guide/web-application/web-application-inputAndOutput.json#s11`
