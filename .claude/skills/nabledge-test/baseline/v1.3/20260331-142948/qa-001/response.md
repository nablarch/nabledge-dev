**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用します。`codeId` 属性でコードIDを指定し、CODE_PATTERNテーブルとCODE_NAMEテーブルから選択項目リストを自動取得してHTMLのselectタグを出力します。

**根拠**:

```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

| 属性名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID |
| pattern | | (指定なし) | CODE_PATTERNテーブルの絞り込みカラム名 |
| labelPattern | | $NAME$ | ラベル整形パターン。`$VALUE$`（コード値）、`$NAME$`（コード名称）など |
| withNoneOption | | false | 先頭に「選択なし」を追加するか |

参照: `guide/web-application/web-application-inputAndOutput.json#s3`, `component/libraries/libraries-07_TagReference.json#s14`
