**結論**: コードリストのプルダウン入力を実装するには、JSPで `<n:codeSelect>` タグを使用し、`codeId` 属性にコードIDを指定します。コードデータはCODE_PATTERNとCODE_NAMEテーブルから自動取得されます。

主要属性: `name`(必須), `codeId`(必須), `pattern`, `optionColumnName`, `labelPattern`($NAME$/$VALUE$など), `withNoneOption`

コード値として`$VALUE$`プレースホルダが使用可能です。