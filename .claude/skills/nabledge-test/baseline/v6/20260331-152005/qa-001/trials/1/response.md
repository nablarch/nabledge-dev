**結論**: コード値のプルダウン入力には、`n:codeSelect` カスタムタグを使用します。コードIDを指定するだけでコードテーブルから選択肢を自動生成できます。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" />
```
pattern="PATTERN2"
| `labelPattern` | | ラベル整形パターン（`$NAME$`、`$SHORTNAME$`、`$VALUE$`（コード値）、`$OPTIONALNAME$`） |
| `optionColumnName` | | オプション名称のカラム名 |

```jsp
<n:select listName="industries" elementValueProperty="industryCode" elementLabelProperty="industryName" name="form.industryCode" withNoneOption="true" />
```