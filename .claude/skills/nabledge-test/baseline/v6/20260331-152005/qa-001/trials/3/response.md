**結論**: コード値のプルダウン入力には、`n:codeSelect` カスタムタグを使用します。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```
| `withNoneOption` | - | `true`で選択なしオプションを先頭に追加（デフォルト: `false`） |

n:select listName="industries" elementValueProperty="industryCode" elementLabelProperty="industryName" withNoneOption="true"

コード値 $VALUE$（コード値）