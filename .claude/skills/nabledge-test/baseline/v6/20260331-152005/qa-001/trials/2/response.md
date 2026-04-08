**結論**: コード値のプルダウン入力には `n:codeSelect` カスタムタグを使用します。コードIDを指定するだけでコードマスタからコード一覧を自動取得してプルダウンを表示できます。

## コード値専用のプルダウン: `n:codeSelect`

コードマスタのデータをプルダウンに表示する場合は、`n:codeSelect` タグを使用します。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" cssClass="form-control" />
```

| 属性 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのプロパティ名 |
| `codeId` | ○ | コードID |
| `pattern` | | パターンのカラム名（省略時は全コード値を表示） |
| `labelPattern` | | ラベル整形パターン。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値） |
| `optionColumnName` | | オプション名称のカラム名 |
| `withNoneOption` | | 先頭に選択なしオプションを追加するか（true/false） |

### パターンを指定して表示を絞り込む場合

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

## 参考: 一般リストのプルダウン（`n:select`）

```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="form-select" />
```

参照: `component/libraries/libraries-tag.json#s1`