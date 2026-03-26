**結論**: コードリストのプルダウン入力には `<n:codeSelect>` タグを使用します。`codeId` 属性にコードIDを指定することで、CODE_PATTERNテーブルとCODE_NAMEテーブルから選択肢リストが自動生成されます。

```jsp
<n:codeSelect name="W11AF01.status" codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01" labelPattern="$VALUE$:$NAME$" listFormat="div" />
```
コード値（コード定義ID）はコード管理機能から取得されます。