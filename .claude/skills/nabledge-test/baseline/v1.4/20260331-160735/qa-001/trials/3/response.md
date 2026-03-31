**結論**: コードリストのプルダウン入力を実装するには、`n:codeSelect` タグ（または UIフレームワークの `field:code_pulldown` ウィジェット）を使用します。`codeId` 属性にコードIDを指定することで、CODE_PATTERN テーブルと CODE_NAME テーブルからコード値を取得して `<select>` 要素を生成します。

**根拠**:

**① n:codeSelect タグを使った実装例（JSP）**:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**② field:code_pulldown ウィジェットを使った実装例（UIフレームワーク）**:
```jsp
<field:code_pulldown
  title            = "ユーザIDロック"
  name             = "11AC_W11AC01.userIdLocked"
  codeId           = "C0000001"
  pattern          = "PATTERN01"
  optionColumnName = "OPTION01"
  labelPattern     = "$OPTIONALNAME$">
</field:code_pulldown>
```

**主要属性**:

| 属性 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | name 属性（リクエストパラメータ名） |
| `codeId` | ○ | コードID（CODE_PATTERN/CODE_NAME テーブルのキー） |
| `pattern` | × | 使用するパターンのカラム名（デフォルト: PATTERN01） |
| `optionColumnName` | × | オプション名称のカラム名（デフォルト: OPTION01） |
| `labelPattern` | × | ラベルの書式（デフォルト: `$NAME$`）。`$NAME$`/`$SHORTNAME$`/`$OPTIONALNAME$`/`$VALUE$` を使用可能 |
| `withNoneOption` | × | `true` にすると先頭に選択なしオプションを追加（デフォルト: false） |
| `noneOptionLabel` | × | 選択なしオプションのラベル（withNoneOption=true 時に有効） |

**注意点**:
- `n:codeSelect` タグを使用するには、コードマスタ（CODE_PATTERN テーブル・CODE_NAME テーブル）にコードが登録されている必要があります。
- 先頭に空白要素（選択なし）を追加したい場合は `withNoneOption="true"` を指定します。空白を選択した際は空文字列 (`""`) がリクエストパラメータとして送信されます。
- `optionColumnName` を使用して `$OPTIONALNAME$` プレースホルダーを `labelPattern` に含める場合は、`optionColumnName` 属性の指定が必須です。
- `field:code_pulldown` ウィジェットはローカル動作時、`codeId` が指定されていれば `/js/devtool/resource/コード値定義.js` の内容を使用します。`codeId` と `sample` を両方指定した場合は `sample` が優先されます。

参照: `component/libraries/libraries-07_TagReference.json#s14`, `component/ui-framework/ui-framework-field_code_pulldown.json#s1`, `component/ui-framework/ui-framework-field_code_pulldown.json#s2`, `guide/web-application/web-application-inputAndOutput.json#s3`, `processing-pattern/web-application/web-application-5.json#s1`