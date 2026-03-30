**結論**: コードリストのプルダウン入力には `n:codeSelect` タグを使用します。このタグは HTML の `select` タグ（プルダウン）を出力し、コード管理機能の CODE_NAME テーブルおよび CODE_PATTERN テーブルからコード値を取得して選択項目として表示します。

`n:codeSelect` タグの必須属性は `name` と `codeId` の2つです。

```jsp
<n:codeSelect name="form.status" codeId="0002" />
```

主な属性: name（必須）、codeId（必須）、pattern、labelPattern（$VALUE$/$NAME$/$SHORTNAME$/$OPTIONALNAME$）、withNoneOption、noneOptionLabel、listFormat

参照: `guide/web-application/web-application-inputAndOutput.json#s3`, `component/libraries/libraries-07_TagReference.json#s14`, `component/libraries/libraries-07_DisplayTag.json#s2`
