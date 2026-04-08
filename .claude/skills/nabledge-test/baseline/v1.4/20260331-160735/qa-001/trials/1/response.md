**結論**: コードリストのプルダウン入力を実装するには、`<n:codeSelect>` タグ（またはUIウィジェットの `<field:code_pulldown>`）を使用します。`codeId` 属性にコードIDを指定することで、CODE_PATTERNテーブルとCODE_NAMEテーブルから選択項目リストを自動的に取得してプルダウンを生成します。

**根拠**:

**基本的な実装例（JSP）**:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002"
              pattern="PATTERN2"
              optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**主要な属性**:

| 属性 | 必須 | 説明 |
|------|------|------|
| `name` | ○ | XHTMLのname属性 |
| `codeId` | ○ | コードID（CODE_PATTERNテーブルのコードID） |
| `pattern` | - | 使用するパターンのカラム名（デフォルト: `PATTERN01`） |
| `optionColumnName` | - | 取得するオプション名称のカラム名（デフォルト: `OPTION01`） |
| `labelPattern` | - | ラベル表示書式。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）が使用可能（デフォルト: `$NAME$`） |
| `withNoneOption` | - | `true` にするとリスト先頭に選択なしオプションを追加（デフォルト: `false`） |
| `noneOptionLabel` | - | 選択なしオプションのラベル（`withNoneOption="true"` の場合に有効） |

**先頭に空白要素を追加する場合**:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002"
              withNoneOption="true"
              noneOptionLabel="選択してください" />
```
空白要素を選択した場合、空文字列（`""`）がリクエストパラメータの値として送信されます。

**UIウィジェットを使用する場合（`field:code_pulldown`）**:
```jsp
<field:code_pulldown name="status" codeId="0002" pattern="PATTERN01" />
```
ウィジェット版も `codeId` が必須属性で、`pattern`、`optionColumnName`、`labelPattern`、`withNoneOption` 等の属性が同様に利用できます。

**注意点**:
- `codeId` はCODE_PATTERNテーブルのコードIDで必須属性です。省略するとエラーになります。
- `pattern` を省略した場合はデフォルトの `PATTERN01` が使用されます。意図したパターンを明示的に指定することを推奨します。
- `$OPTIONALNAME$` を `labelPattern` で使用する場合は `optionColumnName` 属性の指定が必須です。
- UIウィジェット版（`field:code_pulldown`）とカスタムタグ版（`n:codeSelect`）は挙動はほぼ同じですが、ローカル動作時は `sample` 属性（ウィジェット版）でダミー値を指定できます。
- 選択項目（プルダウン）以外にラジオボタン形式が必要な場合は `codeRadioButtons` タグ、チェックボックス形式は `codeCheckboxes` タグを使用します。

参照: `guide/web-application/web-application-inputAndOutput.json#s3`, `component/libraries/libraries-07_TagReference.json#s14`, `component/ui-framework/ui-framework-field_code_pulldown.json#s2`, `processing-pattern/web-application/web-application-5.json#s1`