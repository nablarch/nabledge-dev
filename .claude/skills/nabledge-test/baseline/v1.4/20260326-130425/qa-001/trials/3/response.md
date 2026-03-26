**結論**: コードリストのプルダウン入力を実装するには `n:codeSelect` タグを使用します。`codeId` 属性でコードIDを指定することで、コード値から選択肢リストを取得してHTMLのselectタグとして出力されます。

```jsp
<n:codeSelect name="W11AF01.status" codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01" labelPattern="$VALUE$:$NAME$" />
```